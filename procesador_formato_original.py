import pandas as pd
import numpy as np

class ProcesadorFormatoOriginal:
    def __init__(self):
        pass
    
    def procesar_archivo(self, archivo_path):
        """Procesa archivos con el formato original de costos"""
        try:
            df = pd.read_excel(archivo_path)
            print(f"📄 Archivo cargado: {archivo_path}")
            print(f"📊 Dimensiones: {df.shape}")
            
            # Verificar si tiene el formato original
            columnas_originales = [
                'Nombre', 'SKU', 'Precio FOB (USD)', 'Cantidad Total', 
                'Piezas por Caja', 'Peso por Caja (kg)', 'Largo (cm)', 
                'Ancho (cm)', 'Alto (cm)', 'DDI (%)'
            ]
            
            if all(col in df.columns for col in columnas_originales):
                print("✅ Formato original detectado")
                return self._procesar_formato_original(df)
            else:
                print("❌ No es formato original")
                return None
                
        except Exception as e:
            print(f"❌ Error procesando archivo: {e}")
            return None
    
    def _procesar_formato_original(self, df):
        """Procesa el formato original de costos"""
        productos = []
        
        for idx, row in df.iterrows():
            try:
                # Calcular CBM por caja
                largo = row['Largo (cm)'] / 100  # Convertir a metros
                ancho = row['Ancho (cm)'] / 100
                alto = row['Alto (cm)'] / 100
                cbm_por_caja = largo * ancho * alto
                
                # Calcular CBM total
                cajas_totales = row['Cantidad Total'] / row['Piezas por Caja']
                cbm_total = cbm_por_caja * cajas_totales
                
                # Calcular peso total
                peso_total = row['Peso por Caja (kg)'] * cajas_totales
                
                # Debug: Verificar el valor del DDI
                ddi_valor = row['DDI (%)'] if 'DDI (%)' in row else 18.0
                print(f"🔍 Producto: {row['Nombre']}, DDI leído: {ddi_valor}, Tipo: {type(ddi_valor)}")
                
                # Corregir interpretación del DDI: si es menor a 1, multiplicar por 100
                if isinstance(ddi_valor, (int, float)) and ddi_valor < 1:
                    ddi_valor = ddi_valor * 100
                    print(f"🔧 DDI corregido: {ddi_valor}%")
                
                producto = {
                    'Nombre': row['Nombre'],
                    'SKU': row['SKU'],
                    'Cantidad por Carton': row['Cantidad Total'],
                    'Precio En USD': row['Precio FOB (USD)'],
                    'CBM': cbm_total,
                    'GW': peso_total,
                    'DDI (%)': ddi_valor  # Incluir DDI específico
                }
                
                # Validar datos mínimos
                if (producto['Cantidad por Carton'] > 0 and 
                    producto['Precio En USD'] > 0 and 
                    producto['CBM'] > 0):
                    productos.append(producto)
                    
            except Exception as e:
                print(f"⚠️ Error procesando fila {idx+1}: {e}")
                continue
        
        print(f"✅ Productos procesados: {len(productos)}")
        return productos

# Función de utilidad para usar en Streamlit
def procesar_archivo_formato_original(archivo):
    """Función para usar en Streamlit que procesa archivos con formato original"""
    procesador = ProcesadorFormatoOriginal()
    
    # Guardar archivo temporalmente
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        # Escribir el contenido del archivo
        tmp_file.write(archivo.read())
        tmp_file.flush()
        tmp_path = tmp_file.name
    
    try:
        productos = procesador.procesar_archivo(tmp_path)
        return productos
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

# Función alternativa que recibe el DataFrame directamente
def procesar_dataframe_formato_original(df):
    """Función para procesar DataFrame con formato original"""
    procesador = ProcesadorFormatoOriginal()
    
    # Verificar si tiene el formato original
    columnas_originales = [
        'Nombre', 'SKU', 'Precio FOB (USD)', 'Cantidad Total', 
        'Piezas por Caja', 'Peso por Caja (kg)', 'Largo (cm)', 
        'Ancho (cm)', 'Alto (cm)', 'DDI (%)'
    ]
    
    if all(col in df.columns for col in columnas_originales):
        print("✅ Formato original detectado")
        return procesador._procesar_formato_original(df)
    else:
        print("❌ No es formato original")
        return None 