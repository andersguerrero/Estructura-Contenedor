import pandas as pd
import numpy as np
import re

class ProcesadorArchivosProveedores:
    def __init__(self):
        self.patrones_campos = {
            'nombre': [
                r'商品', r'product', r'item', r'name', r'description', r'desc',
                r'产品', r'名称', r'品名', r'商品名称', r'product name', r'item name'
            ],
            'sku': [
                r'sku', r'item no', r'item number', r'code', r'编号', r'货号',
                r'product code', r'item code', r'商品编号', r'产品编号'
            ],
            'cantidad': [
                r'quantity', r'qty', r'amount', r'数量', r'件数', r'数量',
                r'pcs', r'pieces', r'carton', r'box', r'箱数', r'箱'
            ],
            'precio': [
                r'price', r'cost', r'单价', r'价格', r'cost price', r'unit price',
                r'price per', r'price/pc', r'price per piece', r'价格/件'
            ],
            'cbm': [
                r'cbm', r'volume', r'体积', r'总体积', r'cubic', r'm3',
                r'cubic meter', r'volume m3', r'体积（m3）', r'总体积（m3）'
            ],
            'peso': [
                r'weight', r'g.w.', r'gross weight', r'重量', r'毛重', r'kg',
                r'weight kg', r'gross weight kg', r'总毛重（kg）', r'重量（kg）'
            ]
        }
    
    def detectar_estructura_archivo(self, df):
        """Detecta automáticamente la estructura del archivo de proveedor"""
        print("🔍 Analizando estructura del archivo...")
        
        # Buscar encabezados de tabla
        encabezados_encontrados = {}
        fila_encabezados = None
        
        for i in range(min(20, len(df))):  # Buscar en primeras 20 filas
            fila = df.iloc[i]
            for j, valor in enumerate(fila):
                if pd.notna(valor):
                    valor_str = str(valor).lower()
                    
                    # Buscar patrones de encabezados
                    for campo, patrones in self.patrones_campos.items():
                        for patron in patrones:
                            if patron in valor_str:
                                encabezados_encontrados[campo] = j
                                fila_encabezados = i
                                print(f"✅ Encontrado {campo} en columna {j}: '{valor}'")
                                break
                        if campo in encabezados_encontrados:
                            break
        
        # Si no se encontraron encabezados, verificar si es un archivo simple
        if not encabezados_encontrados:
            # Verificar si el archivo tiene columnas estándar
            columnas_estandar = ['Nombre', 'Cantidad por Carton', 'Precio En USD', 'CBM', 'GW']
            if all(col in df.columns for col in columnas_estandar):
                print("🔧 Archivo con formato estándar detectado...")
                encabezados_encontrados = {
                    'nombre': 'Nombre',
                    'cantidad': 'Cantidad por Carton',
                    'precio': 'Precio En USD',
                    'cbm': 'CBM',
                    'peso': 'GW'
                }
                # Agregar SKU solo si existe
                if 'SKU' in df.columns:
                    encabezados_encontrados['sku'] = 'SKU'
                fila_encabezados = 0  # Los datos empiezan desde la primera fila
            else:
                print("🔧 Usando estructura conocida para archivos de proveedores chinos...")
                # Estructura típica de archivos chinos
                encabezados_encontrados = {
                    'sku': 1,      # Columna 1: SKU/Código
                    'nombre': 2,   # Columna 2: Descripción
                    'cantidad': 5, # Columna 5: QTY/CTN
                    'precio': 6,   # Columna 6: Precio RMB
                    'cbm': 8,      # Columna 8: CBM
                    'peso': 9      # Columna 9: G.W.
                }
                fila_encabezados = 4  # Fila 4 contiene los encabezados
        
        print(f"📋 Fila de encabezados: {fila_encabezados}")
        return {
            'encabezados': encabezados_encontrados,
            'fila_encabezados': fila_encabezados,
            'datos_inicio': fila_encabezados + 1 if fila_encabezados is not None else 0
        }
    
    def extraer_datos_productos(self, df, estructura):
        """Extrae los datos de productos basándose en la estructura detectada"""
        if not estructura:
            return None
        
        productos = []
        encabezados = estructura['encabezados']
        inicio_datos = estructura['datos_inicio']
        
        print(f"📦 Extrayendo datos desde fila {inicio_datos}...")
        
        for i in range(inicio_datos, len(df)):
            fila = df.iloc[i]
            producto = {}
            
            # Extraer datos según los encabezados encontrados
            for campo, col_ref in encabezados.items():
                if isinstance(col_ref, int):
                    # Índice numérico (para archivos chinos)
                    valor = fila.iloc[col_ref]
                else:
                    # Nombre de columna (para archivos estándar)
                    valor = fila[col_ref]
                
                if pd.notna(valor):
                    producto[campo] = valor
            
            # Validar que sea una fila de producto válida
            # Debe tener al menos nombre y algún dato numérico
            if ('nombre' in producto and 
                len(producto) > 1 and 
                self._es_fila_producto_valida(fila)):
                productos.append(producto)
        
        print(f"✅ Extraídos {len(productos)} productos")
        return productos
    
    def _es_fila_producto_valida(self, fila):
        """Verifica si una fila contiene datos válidos de producto"""
        # Debe tener al menos un número en las columnas de datos
        numeros_encontrados = 0
        for valor in fila:
            if pd.notna(valor):
                try:
                    num = float(str(valor))
                    if 0 < num < 10000:  # Rango razonable para datos de producto
                        numeros_encontrados += 1
                except:
                    pass
        
        return numeros_encontrados >= 3  # Al menos 3 números para ser válida
    
    def normalizar_datos(self, productos):
        """Normaliza los datos extraídos al formato estándar"""
        productos_normalizados = []
        
        for producto in productos:
            normalizado = {
                'Nombre': producto.get('nombre', 'Producto Sin Nombre'),
                'SKU': producto.get('sku', f'SKU{len(productos_normalizados)+1:03d}'),
                'Cantidad por Carton': self._extraer_numero(producto.get('cantidad', 1)),
                'Precio En USD': self._extraer_precio(producto.get('precio', 0)),
                'CBM': self._extraer_numero(producto.get('cbm', 0)),
                'GW': self._extraer_numero(producto.get('peso', 0))
            }
            
            # Validar que tenga datos mínimos
            if (normalizado['Cantidad por Carton'] > 0 and 
                (normalizado['Precio En USD'] > 0 or normalizado['CBM'] > 0)):
                productos_normalizados.append(normalizado)
        
        return productos_normalizados
    
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
    
    def _extraer_precio(self, valor):
        """Extrae precio, manejando diferentes formatos"""
        if pd.isna(valor):
            return 0
        
        valor_str = str(valor).lower()
        
        # Detectar si es RMB
        if any(moneda in valor_str for moneda in ['rmb', '¥', '元', '人民币']):
            precio = self._extraer_numero(valor)
            return precio / 7.10  # Convertir RMB a USD
        
        return self._extraer_numero(valor)
    
    def procesar_archivo(self, archivo_path):
        """Procesa un archivo de proveedor y retorna datos normalizados"""
        try:
            df = pd.read_excel(archivo_path)
            print(f"📄 Archivo cargado: {archivo_path}")
            print(f"📊 Dimensiones: {df.shape}")
            
            # Detectar estructura
            estructura = self.detectar_estructura_archivo(df)
            if not estructura:
                return None
            
            # Extraer datos
            productos = self.extraer_datos_productos(df, estructura)
            if not productos:
                return None
            
            # Normalizar datos
            productos_normalizados = self.normalizar_datos(productos)
            
            print(f"🎯 Productos procesados: {len(productos_normalizados)}")
            return productos_normalizados
            
        except Exception as e:
            print(f"❌ Error procesando archivo: {e}")
            return None

# Función de utilidad para usar en Streamlit
def procesar_archivo_proveedor(archivo):
    """Función para usar en Streamlit que procesa archivos de proveedores"""
    procesador = ProcesadorArchivosProveedores()
    
    # Guardar archivo temporalmente
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        archivo.write(tmp_file.name)
        tmp_path = tmp_file.name
    
    try:
        productos = procesador.procesar_archivo(tmp_path)
        return productos
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.unlink(tmp_path) 