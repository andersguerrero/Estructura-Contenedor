import pandas as pd
import numpy as np
import re

class ProcesadorArchivosChinos:
    def __init__(self):
        pass
    
    def procesar_archivo(self, archivo_path):
        """Procesa archivos de proveedores chinos con estructura conocida"""
        try:
            df = pd.read_excel(archivo_path)
            print(f"📄 Archivo cargado: {archivo_path}")
            print(f"📊 Dimensiones: {df.shape}")
            
            # Buscar la fila que contiene los encabezados
            fila_encabezados = self._encontrar_fila_encabezados(df)
            if fila_encabezados is None:
                print("❌ No se encontraron encabezados")
                return None
            
            print(f"📋 Fila de encabezados encontrada: {fila_encabezados}")
            
            # Extraer productos desde la fila siguiente
            productos = self._extraer_productos(df, fila_encabezados + 1)
            
            if productos:
                print(f"✅ Productos extraídos: {len(productos)}")
                return productos
            else:
                print("❌ No se pudieron extraer productos")
                return None
                
        except Exception as e:
            print(f"❌ Error procesando archivo: {e}")
            return None
    
    def _encontrar_fila_encabezados(self, df):
        """Encuentra la fila que contiene los encabezados de la tabla"""
        for i in range(min(10, len(df))):
            fila = df.iloc[i]
            texto_fila = ' '.join([str(v) for v in fila if pd.notna(v)]).lower()
            
            # Buscar patrones que indiquen encabezados
            if any(palabra in texto_fila for palabra in ['qty/ctn', 'price', 'cbm', 'g.w.', '装箱量', '价格', '体积', '重量']):
                print(f"✅ Encabezados encontrados en fila {i}")
                return i
            
            # Buscar patrones específicos de este archivo
            if any(palabra in texto_fila for palabra in ['序号', 'item no', 'description', 'ctn', 'qty/ctn', 'price', 'cbm', 'g.w.']):
                print(f"✅ Encabezados encontrados en fila {i}")
                return i
            
            # También buscar patrones numéricos que indiquen datos de productos
            # Si encontramos una fila con varios números, puede ser la primera fila de datos
            numeros_en_fila = 0
            for valor in fila:
                if pd.notna(valor):
                    try:
                        num = float(str(valor))
                        if 0 < num < 10000:  # Rango razonable
                            numeros_en_fila += 1
                    except:
                        pass
            
            # Si hay suficientes números, puede ser la primera fila de datos
            if numeros_en_fila >= 3:
                print(f"✅ Primera fila de datos encontrada en fila {i}")
                return i - 1  # La fila anterior sería la de encabezados
        
        # Si no encontramos patrones específicos, buscar la primera fila con datos numéricos
        for i in range(min(15, len(df))):
            fila = df.iloc[i]
            numeros_en_fila = 0
            texto_en_fila = 0
            
            for valor in fila:
                if pd.notna(valor):
                    try:
                        num = float(str(valor))
                        if 0 < num < 10000:
                            numeros_en_fila += 1
                    except:
                        if isinstance(valor, str) and len(str(valor)) > 2:
                            texto_en_fila += 1
            
            # Si hay una mezcla de números y texto, puede ser una fila de datos
            if numeros_en_fila >= 2 and texto_en_fila >= 1:
                print(f"✅ Fila de datos encontrada en fila {i}")
                return i - 1  # La fila anterior sería la de encabezados
        
        return None
    
    def _extraer_productos(self, df, inicio_datos):
        """Extrae productos desde la fila especificada"""
        productos = []
        
        for i in range(inicio_datos, len(df)):
            fila = df.iloc[i]
            
            # Verificar si es una fila de producto válida
            if self._es_fila_producto_valida(fila):
                producto = self._extraer_producto_individual(fila)
                if producto:
                    productos.append(producto)
        
        return productos
    
    def _es_fila_producto_valida(self, fila):
        """Verifica si una fila contiene datos válidos de producto"""
        # Debe tener al menos 3 números en las columnas de datos
        numeros_encontrados = 0
        for valor in fila:
            if pd.notna(valor):
                try:
                    num = float(str(valor))
                    if 0 < num < 10000:  # Rango razonable
                        numeros_encontrados += 1
                except:
                    pass
        
        return numeros_encontrados >= 3
    
    def _extraer_producto_individual(self, fila):
        """Extrae un producto individual de una fila"""
        try:
            # Hacer el procesador más flexible para diferentes estructuras
            datos_encontrados = {}
            
            # Buscar nombre (generalmente en las primeras columnas)
            for i in range(min(5, len(fila))):
                valor = fila.iloc[i]
                if pd.notna(valor) and isinstance(valor, str) and len(str(valor)) > 2:
                    # Si no es numérico y tiene suficiente longitud, puede ser nombre
                    try:
                        float(str(valor))
                    except:
                        datos_encontrados['nombre'] = str(valor)
                        datos_encontrados['nombre_pos'] = i
                        break
            
            # Buscar números en diferentes posiciones
            numeros_encontrados = []
            for i in range(len(fila)):
                valor = fila.iloc[i]
                if pd.notna(valor):
                    numero = self._extraer_numero(valor)
                    if numero > 0:
                        numeros_encontrados.append((i, numero))
            
            # Clasificar números por rango típico
            cantidad = 0
            precio_rmb = 0
            cbm = 0
            peso = 0
            sku = ""
            
            for pos, num in numeros_encontrados:
                if 1 <= num <= 1000:  # Cantidad típica
                    cantidad = num
                elif 1 <= num <= 100:  # Precio RMB típico
                    precio_rmb = num
                elif 0.001 <= num <= 1:  # CBM típico
                    cbm = num
                elif 0.1 <= num <= 50:  # Peso típico
                    peso = num
                elif 10000 <= num <= 99999:  # SKU típico
                    sku = str(int(num))
            
            # Validar datos mínimos
            if (datos_encontrados.get('nombre') and cantidad > 0 and (precio_rmb > 0 or cbm > 0)):
                return {
                    'Nombre': datos_encontrados['nombre'],
                    'SKU': sku if sku else f"SKU_{len(datos_encontrados['nombre'])}",
                    'Cantidad por Carton': cantidad,
                    'Precio En USD': precio_rmb / 7.10,  # Convertir RMB a USD
                    'CBM': cbm,
                    'GW': peso
                }
        
        except Exception as e:
            print(f"⚠️ Error extrayendo producto: {e}")
        
        return None
    
    def _extraer_numero(self, valor):
        """Extrae un número de un valor que puede contener texto"""
        if pd.isna(valor):
            return 0
        
        valor_str = str(valor)
        # Buscar números en el texto
        numeros = re.findall(r'[\d,]+\.?\d*', valor_str)
        if numeros:
            try:
                return float(numeros[0].replace(',', ''))
            except:
                return 0
        return 0

# Función de utilidad para usar en Streamlit
def procesar_archivo_proveedor_chino(archivo):
    """Función para usar en Streamlit que procesa archivos de proveedores chinos"""
    procesador = ProcesadorArchivosChinos()
    
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
def procesar_dataframe_proveedor_chino(df):
    """Función para procesar DataFrame de proveedor chino"""
    procesador = ProcesadorArchivosChinos()
    
    # Verificar si tiene características de archivo chino
    # Buscar texto en chino o patrones típicos
    texto_completo = df.to_string()
    caracteristicas_chinas = any(palabra in texto_completo.lower() for palabra in [
        'quotation', '装箱量', '价格', '体积', '重量', 'qty/ctn', 'price', 'cbm', 'g.w.'
    ])
    
    # También verificar si tiene columnas Unnamed (típico de archivos chinos mal leídos)
    columnas_unnamed = [col for col in df.columns if 'unnamed' in col.lower()]
    tiene_unnamed = len(columnas_unnamed) > 0
    
    # Verificar si hay caracteres chinos en los datos
    caracteres_chinos = False
    for col in df.columns:
        if df[col].dtype == 'object':
            valores_texto = df[col].astype(str).str.cat(sep=' ')
            if any('\u4e00' <= char <= '\u9fff' for char in valores_texto):  # Rango de caracteres chinos
                caracteres_chinos = True
                break
    
    if caracteristicas_chinas or (tiene_unnamed and caracteres_chinos):
        print("✅ Características de archivo chino detectadas")
        return procesar_dataframe_chino(df)
    else:
        print("❌ No es archivo chino")
        return None

def procesar_dataframe_chino(df):
    """Procesa un DataFrame como archivo chino"""
    procesador = ProcesadorArchivosChinos()
    
    try:
        print(f"📄 Procesando DataFrame chino: {df.shape}")
        
        # Encontrar fila de encabezados
        fila_encabezados = procesador._encontrar_fila_encabezados(df)
        
        if fila_encabezados is not None:
            print(f"📋 Fila de encabezados encontrada: {fila_encabezados}")
            
            # Extraer productos desde la fila siguiente
            productos = procesador._extraer_productos(df, fila_encabezados + 1)
            print(f"✅ Productos extraídos: {len(productos)}")
            return productos
        else:
            print("❌ No se encontraron encabezados")
            return None
            
    except Exception as e:
        print(f"❌ Error procesando archivo chino: {e}")
        return None 