import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import io
import hashlib
import json

# Configuración de la página
st.set_page_config(
    page_title="Inventario - Valor de Stock",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones para manejo de archivos persistentes
def get_file_hash(file_content):
    """Generar hash único para el archivo"""
    return hashlib.md5(file_content).hexdigest()

def save_uploaded_file(file_content, filename):
    """Guardar archivo subido en la carpeta persistent_files"""
    persistent_dir = "persistent_files"
    if not os.path.exists(persistent_dir):
        os.makedirs(persistent_dir)
    
    file_hash = get_file_hash(file_content)
    file_extension = os.path.splitext(filename)[1]
    saved_filename = f"inventario_{file_hash}{file_extension}"
    file_path = os.path.join(persistent_dir, saved_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path, file_hash

def load_uploaded_files_metadata():
    """Cargar metadatos de archivos subidos del módulo inventario"""
    metadata_file = "persistent_files/inventario_metadata.json"
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
                # Asegurar que sea un diccionario
                if isinstance(data, dict):
                    return data
                else:
                    return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_uploaded_files_metadata(metadata):
    """Guardar metadatos de archivos subidos del módulo inventario"""
    persistent_dir = "persistent_files"
    if not os.path.exists(persistent_dir):
        os.makedirs(persistent_dir)
    
    metadata_file = os.path.join(persistent_dir, "inventario_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def get_inventario_file_info():
    """Obtener información del archivo de inventario guardado"""
    try:
        metadata = load_uploaded_files_metadata()
        if isinstance(metadata, dict):
            return metadata.get('inventario_file', {})
        else:
            return {}
    except Exception:
        return {}

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .total-section {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def get_contenedor_productos():
    """Obtener productos del módulo contenedor"""
    try:
        # Intentar obtener datos calculados del módulo de contenedor completo
        if hasattr(st.session_state, 'df_productos_calculado') and st.session_state.df_productos_calculado is not None:
            df_calculado = st.session_state.df_productos_calculado.copy()
            # st.info("✅ Usando datos calculados del módulo de contenedor completo")
        elif hasattr(st.session_state, 'productos') and st.session_state.productos:
            productos = st.session_state.productos
            df_calculado = pd.DataFrame(productos)
            # st.info("✅ Usando datos del session_state")
        elif os.path.exists('productos_guardados.csv'):
            df_csv = pd.read_csv('productos_guardados.csv')
            productos = df_csv.to_dict('records')
            df_calculado = pd.DataFrame(productos)
            # st.info("✅ Usando datos del CSV guardado")
        else:
            st.warning("⚠️ No hay productos disponibles para calcular")
            return pd.DataFrame()

        if df_calculado.empty:
            st.warning("⚠️ No hay productos disponibles para calcular")
            return pd.DataFrame()

        # Mostrar información de debug sobre las columnas disponibles (solo en desarrollo)
        # st.info(f"📋 Columnas disponibles en el contenedor: {list(df_calculado.columns)}")

        if 'Nombre' in df_calculado.columns:
            df_calculado = df_calculado.rename(columns={'Nombre': 'nombre'})
        else:
            st.error("❌ Error: La columna 'Nombre' no existe en los datos")
            return pd.DataFrame()

        if 'SKU' in df_calculado.columns:
            df_calculado = df_calculado.rename(columns={'SKU': 'sku'})

        # Calcular precio unitario final usando los datos del contenedor
        if 'Precio Unitario Final (USD)' in df_calculado.columns:
            df_calculado['costo_unitario'] = df_calculado['Precio Unitario Final (USD)']
            # st.info(f"✅ Usando 'Precio Unitario Final (USD)' del contenedor")
        else:
            # Calcular el precio unitario final usando los datos disponibles
            try:
                # Obtener parámetros del sidebar (valores por defecto si no están disponibles)
                precio_dolar = st.session_state.get('precio_dolar', 1000.0)
                ddi_pct = st.session_state.get('ddi_pct', 18.0)
                tasas_pct = st.session_state.get('tasas_pct', 3.0)
                iva_pct = st.session_state.get('iva_pct', 21.0)
                iva_adic_pct = st.session_state.get('iva_adic_pct', 20.0)
                ganancias_pct = st.session_state.get('ganancias_pct', 6.0)
                iibb_pct = st.session_state.get('iibb_pct', 2.0)
                seguro_pct = st.session_state.get('seguro_pct', 0.5)
                agente_pct = st.session_state.get('agente_pct', 4.0)
                despachante_pct = st.session_state.get('despachante_pct', 1.0)
                
                # Calcular costos básicos
                df_calculado['FOB (USD)'] = df_calculado['Precio FOB (USD)'] * df_calculado['Cantidad Total']
                df_calculado['Seguro (USD)'] = df_calculado['FOB (USD)'] * (seguro_pct / 100)
                
                # CIF = FOB + Seguro + Flete (si existe)
                if 'Flete por Producto (USD)' in df_calculado.columns:
                    df_calculado['CIF (USD)'] = df_calculado['FOB (USD)'] + df_calculado['Seguro (USD)'] + df_calculado['Flete por Producto (USD)']
                else:
                    df_calculado['CIF (USD)'] = df_calculado['FOB (USD)'] + df_calculado['Seguro (USD)']
                
                # DDI
                df_calculado['DDI (USD)'] = df_calculado['CIF (USD)'] * (ddi_pct / 100)
                
                # Tasas
                df_calculado['Tasas (USD)'] = df_calculado['CIF (USD)'] * (tasas_pct / 100)
                
                # Antidumping (si existe)
                if 'Antidumping (USD)' in df_calculado.columns:
                    df_calculado['Antidumping (USD)'] = df_calculado['Antidumping (USD)'].fillna(0)
                else:
                    df_calculado['Antidumping (USD)'] = 0
                
                # Valor IVA
                df_calculado['Valor IVA (USD)'] = df_calculado['CIF (USD)'] + df_calculado['DDI (USD)'] + df_calculado['Tasas (USD)']
                
                # Impuestos sobre VALOR IVA
                df_calculado['IVA (USD)'] = df_calculado['Valor IVA (USD)'] * (iva_pct / 100)
                df_calculado['IVA Adicional (USD)'] = df_calculado['Valor IVA (USD)'] * (iva_adic_pct / 100)
                df_calculado['Ganancias (USD)'] = df_calculado['Valor IVA (USD)'] * (ganancias_pct / 100)
                df_calculado['IIBB (USD)'] = df_calculado['Valor IVA (USD)'] * (iibb_pct / 100)
                
                # Otros gastos sobre FOB
                df_calculado['Agente (USD)'] = df_calculado['FOB (USD)'] * (agente_pct / 100)
                df_calculado['Despachante (USD)'] = df_calculado['FOB (USD)'] * (despachante_pct / 100)
                
                # Costo con impuestos
                df_calculado['Costo con Impuestos (USD)'] = (df_calculado['CIF (USD)'] + df_calculado['DDI (USD)'] + 
                                                           df_calculado['Tasas (USD)'] + df_calculado['Antidumping (USD)'] + 
                                                           df_calculado['Ganancias (USD)'] + df_calculado['IIBB (USD)'] + 
                                                           df_calculado['Agente (USD)'] + df_calculado['Despachante (USD)'])
                
                # Gastos fijos (si existen)
                if 'Gastos Fijos por Producto (USD)' in df_calculado.columns:
                    df_calculado['Costo Final por Producto (USD)'] = df_calculado['Costo con Impuestos (USD)'] + df_calculado['Gastos Fijos por Producto (USD)']
                else:
                    df_calculado['Costo Final por Producto (USD)'] = df_calculado['Costo con Impuestos (USD)']
                
                # Precio unitario final
                df_calculado['Precio Unitario Final (USD)'] = df_calculado['Costo Final por Producto (USD)'] / df_calculado['Cantidad Total']
                df_calculado['costo_unitario'] = df_calculado['Precio Unitario Final (USD)']
                
                # Mostrar información de debug (solo en desarrollo)
                # st.info(f"✅ Calculado 'Precio Unitario Final (USD)' usando datos del contenedor")
                # if not df_calculado.empty:
                #     st.info(f"📊 Ejemplo de valores calculados:")
                #     st.info(f"   - Producto: {df_calculado.iloc[0].get('nombre', 'N/A')}")
                #     st.info(f"   - Costo Final por Producto: ${df_calculado.iloc[0].get('Costo Final por Producto (USD)', 0):,.2f} USD")
                #     st.info(f"   - Cantidad Total: {df_calculado.iloc[0].get('Cantidad Total', 0):,.0f}")
                #     st.info(f"   - Precio Unitario Final: ${df_calculado.iloc[0].get('Precio Unitario Final (USD)', 0):,.2f} USD")
                
            except Exception as e:
                st.warning(f"⚠️ Error calculando precio unitario final: {e}")
                df_calculado['costo_unitario'] = 0

        # Obtener impuestos recuperables por producto
        impuestos_columns = [
            'IVA (USD)', 'IVA Adicional (USD)', 'Ganancias (USD)', 'IIBB (USD)',
            'Agente (USD)', 'Despachante (USD)', 'Cantidad Total'
        ]
        
        for col in impuestos_columns:
            if col in df_calculado.columns:
                df_calculado[col] = pd.to_numeric(df_calculado[col], errors='coerce').fillna(0)
            else:
                df_calculado[col] = 0

        # Calcular impuestos recuperables por unidad
        if 'Cantidad Total' in df_calculado.columns:
            df_calculado['iva_unitario'] = df_calculado['IVA (USD)'] / df_calculado['Cantidad Total']
            df_calculado['iva_adicional_unitario'] = df_calculado['IVA Adicional (USD)'] / df_calculado['Cantidad Total']
            df_calculado['ganancias_unitario'] = df_calculado['Ganancias (USD)'] / df_calculado['Cantidad Total']
            df_calculado['iibb_unitario'] = df_calculado['IIBB (USD)'] / df_calculado['Cantidad Total']
            df_calculado['agente_unitario'] = df_calculado['Agente (USD)'] / df_calculado['Cantidad Total']
            df_calculado['despachante_unitario'] = df_calculado['Despachante (USD)'] / df_calculado['Cantidad Total']
        else:
            df_calculado['iva_unitario'] = 0
            df_calculado['iva_adicional_unitario'] = 0
            df_calculado['ganancias_unitario'] = 0
            df_calculado['iibb_unitario'] = 0
            df_calculado['agente_unitario'] = 0
            df_calculado['despachante_unitario'] = 0

        # Calcular total de impuestos recuperables por unidad
        df_calculado['impuestos_recuperables_unitario'] = (
            df_calculado['iva_unitario'] + 
            df_calculado['iva_adicional_unitario'] + 
            df_calculado['ganancias_unitario'] + 
            df_calculado['iibb_unitario'] + 
            df_calculado['agente_unitario'] + 
            df_calculado['despachante_unitario']
        )

        if 'sku' not in df_calculado.columns:
            df_calculado['sku'] = df_calculado.index.astype(str).str.zfill(3)

        return df_calculado

    except Exception as e:
        st.error(f"❌ Error cargando productos del contenedor: {e}")
        return pd.DataFrame()

def calculate_inventory_valuation(df_stock, df_contenedor, tipo_cambio):
    """Calcular valuación del inventario usando costos del archivo Excel en USD"""
    if df_stock.empty:
        return pd.DataFrame()
    
    # Procesar datos básicos - incluir SKU, stock y costos del archivo Excel
    required_columns = ['nombre', 'sku', 'stock_actual']
    
    # Verificar si hay columna de costo en el archivo Excel
    if 'costo_unitario_usd' in df_stock.columns:
        required_columns.append('costo_unitario_usd')
        use_excel_cost = True
    else:
        use_excel_cost = False
    
    if 'precio_mayor_unitario' in df_stock.columns:
        required_columns.append('precio_mayor_unitario')
    if 'precio_detal_unitario' in df_stock.columns:
        required_columns.append('precio_detal_unitario')
    
    df_stock_clean = df_stock[required_columns].copy()
    
    # Si no hay costos en el Excel, usar los del contenedor
    if not use_excel_cost and not df_contenedor.empty:
        df_contenedor['sku_normalizado'] = df_contenedor['sku'].str.upper().str.strip()
        df_stock_clean['sku_normalizado'] = df_stock_clean['sku'].str.upper().str.strip()
        
        # Merge con contenedor usando SKU
        df_merged = df_stock_clean.merge(
            df_contenedor[['sku_normalizado', 'costo_unitario', 'sku', 'impuestos_recuperables_unitario',
                          'iva_unitario', 'iva_adicional_unitario', 'ganancias_unitario', 'iibb_unitario',
                          'agente_unitario', 'despachante_unitario']], 
            on='sku_normalizado', 
            how='left',
            suffixes=('', '_contenedor')
        )
    else:
        # Usar costos del archivo Excel
        df_merged = df_stock_clean.copy()
        if use_excel_cost:
            df_merged['costo_unitario'] = df_merged['costo_unitario_usd']
        else:
            df_merged['costo_unitario'] = 0
        
        # Inicializar impuestos recuperables en 0 (no se usan del contenedor)
        df_merged['impuestos_recuperables_unitario'] = 0
        df_merged['iva_unitario'] = 0
        df_merged['iva_adicional_unitario'] = 0
        df_merged['ganancias_unitario'] = 0
        df_merged['iibb_unitario'] = 0
        df_merged['agente_unitario'] = 0
        df_merged['despachante_unitario'] = 0
    
    # Convertir a numérico
    numeric_columns = ['stock_actual', 'costo_unitario', 'impuestos_recuperables_unitario',
                      'iva_unitario', 'iva_adicional_unitario', 'ganancias_unitario', 'iibb_unitario',
                      'agente_unitario', 'despachante_unitario']
    
    # Agregar columnas de precios si existen
    if 'precio_mayor_unitario' in df_merged.columns:
        numeric_columns.append('precio_mayor_unitario')
    if 'precio_detal_unitario' in df_merged.columns:
        numeric_columns.append('precio_detal_unitario')
    
    # Crear precio_venta_unitario basado en precio_detal_unitario o precio_mayor_unitario
    if 'precio_detal_unitario' in df_merged.columns:
        df_merged['precio_venta_unitario'] = df_merged['precio_detal_unitario']
    elif 'precio_mayor_unitario' in df_merged.columns:
        df_merged['precio_venta_unitario'] = df_merged['precio_mayor_unitario']
    else:
        df_merged['precio_venta_unitario'] = 0
    
    numeric_columns.append('precio_venta_unitario')
    
    for col in numeric_columns:
        df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce').fillna(0)
    
    # Cálculos de valuación
    # 1. Costo base (sin impuestos recuperables)
    df_merged['costo_base_total_usd'] = df_merged['stock_actual'] * df_merged['costo_unitario']
    
    # 2. Impuestos recuperables por producto en stock
    df_merged['iva_total_usd'] = df_merged['stock_actual'] * df_merged['iva_unitario']
    df_merged['iva_adicional_total_usd'] = df_merged['stock_actual'] * df_merged['iva_adicional_unitario']
    df_merged['ganancias_total_usd'] = df_merged['stock_actual'] * df_merged['ganancias_unitario']
    df_merged['iibb_total_usd'] = df_merged['stock_actual'] * df_merged['iibb_unitario']
    df_merged['agente_total_usd'] = df_merged['stock_actual'] * df_merged['agente_unitario']
    df_merged['despachante_total_usd'] = df_merged['stock_actual'] * df_merged['despachante_unitario']
    
    # 3. Total impuestos recuperables
    df_merged['impuestos_recuperables_total_usd'] = (
        df_merged['iva_total_usd'] + df_merged['iva_adicional_total_usd'] + 
        df_merged['ganancias_total_usd'] + df_merged['iibb_total_usd'] + 
        df_merged['agente_total_usd'] + df_merged['despachante_total_usd']
    )
    
    # 4. Valuación real del inventario (costo base + impuestos recuperables)
    df_merged['valuacion_real_usd'] = df_merged['costo_base_total_usd'] + df_merged['impuestos_recuperables_total_usd']
    
    # 5. Valores de venta (usando precio_venta_unitario)
    df_merged['valor_venta_total_usd'] = df_merged['stock_actual'] * df_merged['precio_venta_unitario']
    # 6. Ganancia real (venta - valuación real)
    df_merged['ganancia_real_usd'] = df_merged['valor_venta_total_usd'] - df_merged['valuacion_real_usd']
    df_merged['porcentaje_ganancia_real'] = ((df_merged['ganancia_real_usd'] / df_merged['valuacion_real_usd']) * 100).fillna(0)
    
    # 7. Cálculos de ganancias por ámbito (mayor y detal)
    if 'precio_mayor_unitario' in df_merged.columns:
        df_merged['valor_venta_mayor_usd'] = df_merged['stock_actual'] * df_merged['precio_mayor_unitario']
        df_merged['ganancia_mayor_usd'] = df_merged['valor_venta_mayor_usd'] - df_merged['valuacion_real_usd']
        df_merged['porcentaje_ganancia_mayor'] = ((df_merged['ganancia_mayor_usd'] / df_merged['valuacion_real_usd']) * 100).fillna(0)
    else:
        df_merged['valor_venta_mayor_usd'] = 0
        df_merged['ganancia_mayor_usd'] = 0
        df_merged['porcentaje_ganancia_mayor'] = 0
    
    if 'precio_detal_unitario' in df_merged.columns:
        df_merged['valor_venta_detal_usd'] = df_merged['stock_actual'] * df_merged['precio_detal_unitario']
        df_merged['ganancia_detal_usd'] = df_merged['valor_venta_detal_usd'] - df_merged['valuacion_real_usd']
        df_merged['porcentaje_ganancia_detal'] = ((df_merged['ganancia_detal_usd'] / df_merged['valuacion_real_usd']) * 100).fillna(0)
    else:
        df_merged['valor_venta_detal_usd'] = 0
        df_merged['ganancia_detal_usd'] = 0
        df_merged['porcentaje_ganancia_detal'] = 0
    
    # Calcular porcentajes de ganancia en pesos (se recalculan después de los valores en pesos)
    # Estos se calcularán después de que se calculen los valores en pesos
    
    # 8. Valores en pesos - Solo el costo base se actualiza con el tipo de cambio
    df_merged['costo_base_total_pesos'] = df_merged['costo_base_total_usd'] * tipo_cambio
    
    # Los demás valores en pesos se calculan basándose en el nuevo costo en pesos
    # Impuestos recuperables en pesos (mantienen la proporción del costo USD)
    df_merged['impuestos_recuperables_total_pesos'] = df_merged['impuestos_recuperables_total_usd'] * tipo_cambio
    
    # Valuación real en pesos (costo base + impuestos recuperables)
    df_merged['valuacion_real_pesos'] = df_merged['costo_base_total_pesos'] + df_merged['impuestos_recuperables_total_pesos']
    
    # Valores de venta en pesos (se mantienen fijos, no se ven afectados por el tipo de cambio)
    # Si es la primera vez que se calcula, convertir de USD a pesos y guardar como originales
    if 'valor_venta_total_pesos_original' not in df_merged.columns:
        df_merged['valor_venta_total_pesos_original'] = df_merged['valor_venta_total_usd'] * tipo_cambio
        df_merged['valor_venta_mayor_pesos_original'] = df_merged['valor_venta_mayor_usd'] * tipo_cambio
        df_merged['valor_venta_detal_pesos_original'] = df_merged['valor_venta_detal_usd'] * tipo_cambio
    else:
        # Si ya existen los valores originales, mantenerlos fijos (no recalcular)
        pass
    
    # Usar los valores originales fijos (no se recalculan con el tipo de cambio)
    df_merged['valor_venta_total_pesos'] = df_merged['valor_venta_total_pesos_original']
    df_merged['valor_venta_mayor_pesos'] = df_merged['valor_venta_mayor_pesos_original']
    df_merged['valor_venta_detal_pesos'] = df_merged['valor_venta_detal_pesos_original']
    
    # Ganancia real en pesos (se recalcula basándose en la nueva valuación y precios fijos)
    df_merged['ganancia_real_pesos'] = df_merged['valor_venta_total_pesos'] - df_merged['valuacion_real_pesos']
    df_merged['ganancia_mayor_pesos'] = df_merged['valor_venta_mayor_pesos'] - df_merged['valuacion_real_pesos']
    df_merged['ganancia_detal_pesos'] = df_merged['valor_venta_detal_pesos'] - df_merged['valuacion_real_pesos']
    
    # 9. Recalcular porcentajes de ganancia en pesos basándose en los nuevos valores
    df_merged['porcentaje_ganancia_real_pesos'] = ((df_merged['ganancia_real_pesos'] / df_merged['valuacion_real_pesos']) * 100).fillna(0)
    df_merged['porcentaje_ganancia_mayor_pesos'] = ((df_merged['ganancia_mayor_pesos'] / df_merged['valuacion_real_pesos']) * 100).fillna(0)
    df_merged['porcentaje_ganancia_detal_pesos'] = ((df_merged['ganancia_detal_pesos'] / df_merged['valuacion_real_pesos']) * 100).fillna(0)
    
    # 10. Estado del producto
    df_merged['estado'] = 'Normal'
    
    # Marcar productos sin costo
    df_merged.loc[df_merged['costo_unitario'].isna() | (df_merged['costo_unitario'] == 0), 'estado'] = 'Sin costo'
    
    # Marcar productos no vinculados (sin SKU del contenedor)
    if 'sku_contenedor' in df_merged.columns:
        df_merged.loc[df_merged['sku_contenedor'].isna(), 'estado'] = 'No vinculado'
    elif 'sku' in df_merged.columns:
        df_merged.loc[df_merged['sku'].isna(), 'estado'] = 'No vinculado'
    
    # Eliminar columnas que pueden no existir
    columns_to_drop = ['nombre_normalizado']
    for col in columns_to_drop:
        if col in df_merged.columns:
            df_merged = df_merged.drop(col, axis=1)
    
    return df_merged

def calculate_inventory_totals(df):
    """Calcular totales del inventario"""
    if df.empty:
        return {
            'total_costo_base_usd': 0,
            'total_costo_base_pesos': 0,
            'total_impuestos_recuperables_usd': 0,
            'total_impuestos_recuperables_pesos': 0,
            'total_valuacion_real_usd': 0,
            'total_valuacion_real_pesos': 0,
            'total_venta_usd': 0,
            'total_venta_pesos': 0,
            'total_ganancia_real_usd': 0,
            'total_ganancia_real_pesos': 0,
            'total_iva_usd': 0,
            'total_iva_adicional_usd': 0,
            'total_ganancias_usd': 0,
            'total_iibb_usd': 0,
            'total_agente_usd': 0,
            'total_despachante_usd': 0,
            'productos_sin_costo': 0,
            'productos_no_vinculados': 0,
            'total_productos': 0
        }
    
    totals = {
        'total_costo_base_usd': df['costo_base_total_usd'].sum(),
        'total_costo_base_pesos': df['costo_base_total_pesos'].sum(),
        'total_impuestos_recuperables_usd': df['impuestos_recuperables_total_usd'].sum(),
        'total_impuestos_recuperables_pesos': df['impuestos_recuperables_total_pesos'].sum(),
        'total_valuacion_real_usd': df['valuacion_real_usd'].sum(),
        'total_valuacion_real_pesos': df['valuacion_real_pesos'].sum(),
        'total_venta_usd': df['valor_venta_total_usd'].sum(),
        'total_venta_pesos': df['valor_venta_total_pesos'].sum(),
        'total_ganancia_real_usd': df['ganancia_real_usd'].sum(),
        'total_ganancia_real_pesos': df['ganancia_real_pesos'].sum(),
        'total_iva_usd': df['iva_total_usd'].sum(),
        'total_iva_adicional_usd': df['iva_adicional_total_usd'].sum(),
        'total_ganancias_usd': df['ganancias_total_usd'].sum(),
        'total_iibb_usd': df['iibb_total_usd'].sum(),
        'total_agente_usd': df['agente_total_usd'].sum(),
        'total_despachante_usd': df['despachante_total_usd'].sum(),
        'productos_sin_costo': len(df[df['estado'] == 'Sin costo']),
        'productos_no_vinculados': len(df[df['estado'] == 'No vinculado']),
        'total_productos': len(df)
    }
    
    return totals

# Header principal
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800;">📦 Inventario - Valor de Stock</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
        Cálculo del valor total del inventario cruzando datos del contenedor con stock actual
    </p>
</div>
""", unsafe_allow_html=True)

# Navegación
col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns(5)

with col_nav1:
    if st.button("🏠 Inicio", use_container_width=True):
        st.switch_page("app_costos_final.py")

with col_nav2:
    if st.button("🚢 Contenedor", use_container_width=True):
        st.switch_page("pages/contenedor_completo.py")

with col_nav3:
    if st.button("💰 Ganancias", use_container_width=True):
        st.switch_page("pages/precio_venta.py")

with col_nav4:
    if st.button("📦 Inventario", use_container_width=True, type="primary"):
        st.switch_page("pages/inventario.py")

with col_nav5:
    if st.button("🚀 ML Pro", use_container_width=True):
        st.switch_page("pages/precio_venta_ml_avanzado.py")

# Obtener productos del contenedor
df_contenedor = get_contenedor_productos()

if df_contenedor.empty:
    st.warning("⚠️ No hay productos del contenedor disponibles. Carga productos desde el módulo de contenedor.")
    st.stop()

# SIDEBAR - Configuración y carga de datos
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 1rem;">
        <h3 style="margin: 0; font-size: 1.2rem;">⚙️ Configuración</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Tipo de cambio con valor predeterminado
    tipo_cambio_guardado = st.session_state.get('tipo_cambio_inventario', 1300.0)
    
    tipo_cambio = st.number_input(
        "💱 Tipo de cambio (ARS/USD)",
        min_value=0.0,
        value=tipo_cambio_guardado,
        step=1.0,
        help="Ingresa el tipo de cambio actual para calcular valores en pesos"
    )
    
    st.session_state['tipo_cambio_inventario'] = tipo_cambio
    
    # Verificar si el tipo de cambio cambió y recalcular si es necesario
    if 'tipo_cambio_anterior' not in st.session_state:
        st.session_state['tipo_cambio_anterior'] = tipo_cambio
    elif st.session_state['tipo_cambio_anterior'] != tipo_cambio:
        # El tipo de cambio cambió, recalcular preservando los valores originales de venta
        if 'df_stock' in st.session_state and 'df_processed' in st.session_state:
            df_stock = st.session_state.df_stock
            df_contenedor = get_contenedor_productos()
            
            # Preservar los valores originales de venta si existen
            if 'df_processed' in st.session_state and not st.session_state.df_processed.empty:
                df_anterior = st.session_state.df_processed
                if 'valor_venta_total_pesos_original' in df_anterior.columns:
                    # Crear un DataFrame temporal con los valores originales
                    df_temp = df_anterior[['nombre', 'valor_venta_total_pesos_original', 
                                         'valor_venta_mayor_pesos_original', 'valor_venta_detal_pesos_original']].copy()
                    df_temp = df_temp.set_index('nombre')
            
            df_processed = calculate_inventory_valuation(df_stock, df_contenedor, tipo_cambio)
            
            # Restaurar los valores originales de venta si existen
            if 'df_temp' in locals() and not df_temp.empty:
                for idx, row in df_processed.iterrows():
                    nombre = row['nombre']
                    if nombre in df_temp.index:
                        df_processed.loc[idx, 'valor_venta_total_pesos_original'] = df_temp.loc[nombre, 'valor_venta_total_pesos_original']
                        df_processed.loc[idx, 'valor_venta_mayor_pesos_original'] = df_temp.loc[nombre, 'valor_venta_mayor_pesos_original']
                        df_processed.loc[idx, 'valor_venta_detal_pesos_original'] = df_temp.loc[nombre, 'valor_venta_detal_pesos_original']
                        # Actualizar los valores de venta con los originales
                        df_processed.loc[idx, 'valor_venta_total_pesos'] = df_temp.loc[nombre, 'valor_venta_total_pesos_original']
                        df_processed.loc[idx, 'valor_venta_mayor_pesos'] = df_temp.loc[nombre, 'valor_venta_mayor_pesos_original']
                        df_processed.loc[idx, 'valor_venta_detal_pesos'] = df_temp.loc[nombre, 'valor_venta_detal_pesos_original']
                        # Recalcular ganancias con los valores originales
                        df_processed.loc[idx, 'ganancia_real_pesos'] = df_processed.loc[idx, 'valor_venta_total_pesos'] - df_processed.loc[idx, 'valuacion_real_pesos']
                        df_processed.loc[idx, 'ganancia_mayor_pesos'] = df_processed.loc[idx, 'valor_venta_mayor_pesos'] - df_processed.loc[idx, 'valuacion_real_pesos']
                        df_processed.loc[idx, 'ganancia_detal_pesos'] = df_processed.loc[idx, 'valor_venta_detal_pesos'] - df_processed.loc[idx, 'valuacion_real_pesos']
            
            if not df_processed.empty:
                totals = calculate_inventory_totals(df_processed)
                st.session_state.df_processed = df_processed
                st.session_state.totals = totals
                st.session_state.tipo_cambio = tipo_cambio
                st.session_state['tipo_cambio_anterior'] = tipo_cambio
                st.rerun()
    
    st.session_state['tipo_cambio_anterior'] = tipo_cambio
    
    st.markdown("---")
    
    # Sección de archivo de ejemplo
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
        <h3 style="margin: 0; font-size: 1.2rem; color: #333;">📋 Archivo de Ejemplo</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Descargar archivo de ejemplo
    if os.path.exists('ejemplo_inventario_actualizado.xlsx'):
        with open('ejemplo_inventario_actualizado.xlsx', 'rb') as file:
            st.download_button(
                label="📥 Descargar Ejemplo Excel",
                data=file.read(),
                file_name="ejemplo_inventario_actualizado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Descarga el archivo de ejemplo con las columnas requeridas y opcionales"
            )
        
        st.caption("💡 Incluye: nombre, sku, stock_actual, costo_unitario_usd, precio_mayor_unitario, precio_detal_unitario")
    else:
        st.warning("⚠️ Archivo de ejemplo no encontrado")
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
        <h3 style="margin: 0; font-size: 1.2rem; color: #333;">📤 Cargar Datos</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Nuevo formato**: El archivo Excel puede incluir la columna 'costo_unitario_usd' con los costos en USD. Estos se convertirán automáticamente a ARS según el tipo de cambio.")
    
    # Verificar si hay un archivo guardado previamente
    inventario_file_info = get_inventario_file_info()
    
    # Cargar archivo
    uploaded_file = st.file_uploader(
        "Selecciona tu archivo Excel",
        type=['xlsx', 'xls'],
        help="Columnas requeridas: nombre, sku, stock_actual. Opcionales: costo_unitario_usd, precio_mayor_unitario, precio_detal_unitario"
    )
    
    # Cargar automáticamente el archivo guardado si existe y no hay archivo nuevo subido
    if inventario_file_info and not uploaded_file and 'df_stock' not in st.session_state:
        try:
            file_path = inventario_file_info.get('file_path')
            if file_path and os.path.exists(file_path):
                df_stock = pd.read_excel(file_path)
                st.session_state.df_stock = df_stock
                st.session_state.inventario_file_info = inventario_file_info
                
                # Mostrar información del archivo cargado automáticamente
                st.success(f"""
                🔄 **Archivo cargado automáticamente:**
                - **Nombre:** {inventario_file_info.get('original_name', 'N/A')}
                - **Productos:** {inventario_file_info.get('productos_count', 0)}
                - **Fecha:** {inventario_file_info.get('upload_date', 'N/A')}
                """)
                
                st.rerun()
            else:
                st.warning("⚠️ El archivo guardado no se encuentra")
        except Exception as e:
            st.error(f"❌ Error cargando archivo guardado: {e}")
    
    # Mostrar información del archivo guardado si existe pero ya está cargado
    elif inventario_file_info and not uploaded_file and 'df_stock' in st.session_state:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #155724; font-size: 1rem;">📁 Archivo Cargado</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Información del archivo
        st.markdown(f"""
        **📄 Nombre:** {inventario_file_info.get('original_name', 'N/A')}
        """)
        
        st.markdown(f"""
        **📊 Productos:** {inventario_file_info.get('productos_count', 0)}
        """)
        
        st.markdown(f"""
        **📅 Fecha:** {inventario_file_info.get('upload_date', 'N/A')}
        """)
        
        st.markdown("---")
        
        # Botón de eliminar
        if st.button("🗑️ Eliminar archivo", use_container_width=True, help="Elimina el archivo guardado para cargar uno nuevo"):
            # Limpiar session state
            if 'df_stock' in st.session_state:
                del st.session_state.df_stock
            if 'df_processed' in st.session_state:
                del st.session_state.df_processed
            if 'totals' in st.session_state:
                del st.session_state.totals
            if 'inventario_file_info' in st.session_state:
                del st.session_state.inventario_file_info
            
            # Limpiar metadatos del archivo
            metadata = load_uploaded_files_metadata()
            if 'inventario_file' in metadata:
                del metadata['inventario_file']
                save_uploaded_files_metadata(metadata)
            
            st.success("✅ Archivo eliminado. Puedes cargar un nuevo archivo.")
            st.rerun()
    
    if uploaded_file is not None:
        try:
            # Leer el archivo
            file_content = uploaded_file.read()
            df_stock = pd.read_excel(io.BytesIO(file_content))
            
            required_columns = ['nombre', 'sku', 'stock_actual']
            # Columnas opcionales para mayor y detal
            optional_columns = ['precio_mayor_unitario', 'precio_detal_unitario']
            available_optional = [col for col in optional_columns if col in df_stock.columns]
            
            missing_columns = [col for col in required_columns if col not in df_stock.columns]
            
            if missing_columns:
                st.error(f"❌ Faltan columnas: {', '.join(missing_columns)}")
            else:
                # Guardar archivo
                file_path, file_hash = save_uploaded_file(file_content, uploaded_file.name)
                
                # Guardar metadatos
                metadata = load_uploaded_files_metadata()
                metadata['inventario_file'] = {
                    'file_path': file_path,
                    'file_hash': file_hash,
                    'original_name': uploaded_file.name,
                    'productos_count': len(df_stock),
                    'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'columns': list(df_stock.columns)
                }
                save_uploaded_files_metadata(metadata)
                
                success_msg = f"✅ {len(df_stock)} productos cargados"
                if available_optional:
                    success_msg += f" • Columnas adicionales: {', '.join(available_optional)}"
                st.success(success_msg)
                
                # Guardar en session state
                st.session_state.df_stock = df_stock
                st.session_state.inventario_file_info = metadata['inventario_file']
                
                df_processed = calculate_inventory_valuation(df_stock, df_contenedor, tipo_cambio)
                
                if not df_processed.empty:
                    totals = calculate_inventory_totals(df_processed)
                    
                    st.session_state.df_processed = df_processed
                    st.session_state.totals = totals
                    st.session_state.tipo_cambio = tipo_cambio
                    
                else:
                    st.error("❌ Error procesando los datos")
                    
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    # Procesar datos si están en session state
    if 'df_stock' in st.session_state and 'df_processed' not in st.session_state:
        df_stock = st.session_state.df_stock
        df_processed = calculate_inventory_valuation(df_stock, df_contenedor, tipo_cambio)
        
        if not df_processed.empty:
            totals = calculate_inventory_totals(df_processed)
            
            st.session_state.df_processed = df_processed
            st.session_state.totals = totals
            st.session_state.tipo_cambio = tipo_cambio

# MAIN CONTENT - Mostrar resultados
if 'df_processed' in st.session_state and not st.session_state.df_processed.empty:
    df_processed = st.session_state.df_processed
    totals = st.session_state.totals
    tipo_cambio = st.session_state.tipo_cambio
    
    # Mostrar información de datos cargados
    st.markdown("""
    <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h4 style="margin: 0; color: #155724;">📊 Datos Cargados</h4>
        <p style="margin: 0.5rem 0 0 0; color: #155724;">✅ Inventario cargado con {} productos • Tipo de cambio: ${:,.0f} ARS/USD</p>
    </div>
    """.format(len(df_processed), tipo_cambio), unsafe_allow_html=True)
    
    # Botón para limpiar datos
    if st.button("🗑️ Limpiar Datos", help="Elimina los datos cargados"):
        # Limpiar session state
        if 'df_processed' in st.session_state:
            del st.session_state.df_processed
        if 'totals' in st.session_state:
            del st.session_state.totals
        if 'tipo_cambio' in st.session_state:
            del st.session_state.tipo_cambio
        if 'df_stock' in st.session_state:
            del st.session_state.df_stock
        if 'inventario_file_info' in st.session_state:
            del st.session_state.inventario_file_info
        
        # Limpiar metadatos del archivo
        metadata = load_uploaded_files_metadata()
        if 'inventario_file' in metadata:
            del metadata['inventario_file']
            save_uploaded_files_metadata(metadata)
        
        st.rerun()
    
    # Mostrar productos
    st.markdown("### 📋 Productos del Inventario")
    
    # Filtrar productos con datos válidos
    df_valid = df_processed[df_processed['estado'] == 'Normal'].copy()
    
    if not df_valid.empty:
        # Preparar datos para la tabla
        df_display = df_valid.copy()
        
        # Crear columnas de visualización
        df_display['SKU'] = df_display.apply(lambda row: row.get('sku', row.get('sku_contenedor', 'N/A')), axis=1)
        df_display['Precio Venta (USD)'] = df_display['precio_venta_unitario'].apply(lambda x: f"${x:,.2f}" if x > 0 else "No configurado")
        df_display['Precio Venta (ARS)'] = df_display['precio_venta_unitario'].apply(lambda x: f"${x * tipo_cambio:,.0f}" if x > 0 else "N/A")
        df_display['Costo Base (USD)'] = df_display['costo_unitario'].apply(lambda x: f"${x:,.2f}")
        df_display['Costo Base (ARS)'] = df_display['costo_unitario'].apply(lambda x: f"${x * tipo_cambio:,.0f}")
        df_display['Stock'] = df_display['stock_actual'].apply(lambda x: f"{x:,.0f}")
        df_display['Valuación Real (USD)'] = df_display['valuacion_real_usd'].apply(lambda x: f"${x:,.2f}")
        df_display['Ganancia Real (USD)'] = df_display['ganancia_real_usd'].apply(lambda x: f"${x:,.2f}")
        df_display['Margen (%)'] = df_display['porcentaje_ganancia_real'].apply(lambda x: f"{x:.1f}%")
        
        # Crear columnas adicionales necesarias
        df_display['Precio Mayor (ARS)'] = df_display['precio_mayor_unitario'].apply(lambda x: f"${x * tipo_cambio:,.0f}" if x > 0 else "No configurado")
        
        # Calcular porcentaje de diferencia entre mayor y detal
        def calcular_porcentaje_diferencia(row):
            if (row['precio_detal_unitario'] > 0 and row['precio_mayor_unitario'] > 0):
                diferencia = row['precio_detal_unitario'] - row['precio_mayor_unitario']
                porcentaje = (diferencia / row['precio_detal_unitario']) * 100
                return f"{porcentaje:.1f}%"
            else:
                return "N/A"
        
        df_display['% Diferencia'] = df_display.apply(calcular_porcentaje_diferencia, axis=1)
        
        # Calcular presupuesto unitario en ARS
        def calcular_presupuesto_unitario(row):
            if (row['precio_detal_unitario'] > 0 and row['precio_mayor_unitario'] > 0):
                diferencia_usd = row['precio_detal_unitario'] - row['precio_mayor_unitario']
                presupuesto_ars = diferencia_usd * tipo_cambio
                return f"${presupuesto_ars:,.0f}"
            else:
                return "N/A"
        
        df_display['Presupuesto Unitario (ARS)'] = df_display.apply(calcular_presupuesto_unitario, axis=1)
        
        # Seleccionar solo las columnas requeridas
        columns_to_show = [
            'nombre', 'Costo Base (ARS)', 'Precio Venta (ARS)', 'Precio Mayor (ARS)', '% Diferencia', 'Presupuesto Unitario (ARS)'
        ]
        
        # Filtrar columnas que existen
        available_columns = [col for col in columns_to_show if col in df_display.columns]
        df_table = df_display[available_columns].copy()
        
        # Renombrar columnas para mejor visualización
        column_mapping = {
            'nombre': 'Producto',
            'Costo Base (ARS)': 'Costo ARS',
            'Precio Venta (ARS)': 'Precio Detal ARS',
            'Precio Mayor (ARS)': 'Precio Mayor ARS',
            '% Diferencia': '% Diferencia',
            'Presupuesto Unitario (ARS)': 'Presupuesto ARS'
        }
        
        df_table = df_table.rename(columns=column_mapping)
        
        # Mostrar tabla principal
        st.dataframe(
            df_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Producto": st.column_config.TextColumn("Producto", width="medium"),
                "Costo ARS": st.column_config.TextColumn("Costo ARS", width="small"),
                "Precio Detal ARS": st.column_config.TextColumn("Precio Detal ARS", width="small"),
                "Precio Mayor ARS": st.column_config.TextColumn("Precio Mayor ARS", width="small"),
                "% Diferencia": st.column_config.TextColumn("% Diferencia", width="small"),
                "Presupuesto ARS": st.column_config.TextColumn("Presupuesto ARS", width="small")
            }
        )
        
        # Mostrar expanders para detalles adicionales
        st.markdown("### 🔍 Detalles Adicionales")
        
        # Selector de producto para ver detalles
        productos_list = df_valid['nombre'].tolist()
        producto_seleccionado = st.selectbox(
            "Selecciona un producto para ver detalles completos:",
            productos_list,
            index=0
        )
        
        # Obtener datos del producto seleccionado
        producto_data = df_valid[df_valid['nombre'] == producto_seleccionado].iloc[0]
        
        # Expander con información detallada
        with st.expander(f"📊 Detalles completos: {producto_seleccionado}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**💰 Análisis de Ganancia**")
                st.metric("Valuación Real", f"${producto_data['valuacion_real_usd']:,.2f}", f"${producto_data['valuacion_real_pesos']:,.0f} ARS")
                st.metric("Ganancia Real", f"${producto_data['ganancia_real_usd']:,.2f}", f"${producto_data['ganancia_real_pesos']:,.0f} ARS")
                st.metric("Valor Venta Total", f"${producto_data['valor_venta_total_usd']:,.2f}", f"${producto_data['valor_venta_total_pesos']:,.0f} ARS")
            
            with col2:
                st.markdown("**📊 Información Adicional**")
                valuacion_unitaria_usd = producto_data['valuacion_real_usd'] / producto_data['stock_actual'] if producto_data['stock_actual'] > 0 else 0
                valuacion_unitaria_ars = valuacion_unitaria_usd * tipo_cambio
                st.metric("Valuación Real Unitaria", f"${valuacion_unitaria_usd:,.2f}", f"${valuacion_unitaria_ars:,.0f} ARS")
                
                st.metric("Margen Real", f"{producto_data['porcentaje_ganancia_real']:.1f}%")
                
                # Mostrar información de impuestos solo si es relevante
                if producto_data['impuestos_recuperables_unitario'] > 0:
                    impuestos_ars = producto_data['impuestos_recuperables_unitario'] * tipo_cambio
                    st.metric("Impuestos Recuperables", f"${producto_data['impuestos_recuperables_unitario']:,.2f}", f"${impuestos_ars:,.0f} ARS")
            
            # Información de Mayor/Detal si está disponible
            if 'precio_mayor_unitario' in df_processed.columns or 'precio_detal_unitario' in df_processed.columns:
                 st.markdown("**🏪 Análisis Mayor/Detal**")
                 col_mayor, col_detal = st.columns(2)
                 
                 with col_mayor:
                     if 'precio_mayor_unitario' in df_processed.columns and producto_data['precio_mayor_unitario'] > 0:
                         st.metric("Ganancia al Mayor", f"${producto_data['ganancia_mayor_usd']:,.2f}", f"${producto_data['ganancia_mayor_pesos']:,.0f} ARS")
                         st.metric("Margen al Mayor", f"{producto_data['porcentaje_ganancia_mayor']:.1f}%")
                     else:
                         st.info("ℹ️ No hay precio al mayor configurado")
                 
                 with col_detal:
                     if 'precio_detal_unitario' in df_processed.columns and producto_data['precio_detal_unitario'] > 0:
                         st.metric("Ganancia al Detal", f"${producto_data['ganancia_detal_usd']:,.2f}", f"${producto_data['ganancia_detal_pesos']:,.0f} ARS")
                         st.metric("Margen al Detal", f"{producto_data['porcentaje_ganancia_detal']:.1f}%")
                     else:
                         st.info("ℹ️ No hay precio al detal configurado")
                 
                 # Nueva sección: Diferencia para publicidad
                 if ('precio_mayor_unitario' in df_processed.columns and producto_data['precio_mayor_unitario'] > 0 and 
                     'precio_detal_unitario' in df_processed.columns and producto_data['precio_detal_unitario'] > 0):
                     
                     st.markdown("**📢 Presupuesto de Publicidad**")
                     
                     # Calcular diferencias
                     diferencia_precio_usd = producto_data['precio_detal_unitario'] - producto_data['precio_mayor_unitario']
                     diferencia_precio_ars = diferencia_precio_usd * tipo_cambio
                     
                     # Calcular porcentaje de diferencia
                     if producto_data['precio_detal_unitario'] > 0:
                         porcentaje_diferencia = (diferencia_precio_usd / producto_data['precio_detal_unitario']) * 100
                     else:
                         porcentaje_diferencia = 0
                     
                     # Calcular por unidad y por stock total
                     presupuesto_por_unidad_usd = diferencia_precio_usd
                     presupuesto_por_unidad_ars = diferencia_precio_ars
                     presupuesto_total_usd = presupuesto_por_unidad_usd * producto_data['stock_actual']
                     presupuesto_total_ars = presupuesto_por_unidad_ars * producto_data['stock_actual']
                     
                     col_pub1, col_pub2 = st.columns(2)
                     
                     with col_pub1:
                         st.metric(
                             "Diferencia por Unidad",
                             f"${diferencia_precio_ars:,.0f}",
                             f"${diferencia_precio_usd:,.2f} USD"
                         )
                         st.metric(
                             "Porcentaje Diferencia",
                             f"{porcentaje_diferencia:.1f}%",
                             f"Detal vs Mayor"
                         )
                     
                     with col_pub2:
                         st.metric(
                             "Presupuesto Total",
                             f"${presupuesto_total_ars:,.0f}",
                             f"${presupuesto_total_usd:,.2f} USD"
                         )
                         st.metric(
                             "Presupuesto por Unidad",
                             f"${presupuesto_por_unidad_ars:,.0f}",
                             f"${presupuesto_por_unidad_usd:,.2f} USD"
                         )
                     
                     # Información adicional
                     st.info(f"""
                     💡 **Análisis de Publicidad:**
                     - **Diferencia disponible:** ${diferencia_precio_ars:,.0f} ARS por unidad
                     - **Presupuesto total:** ${presupuesto_total_ars:,.0f} ARS para todo el stock
                     - **Porcentaje de margen:** {porcentaje_diferencia:.1f}% disponible para marketing
                     """)
        
        # Totales del Inventario
        st.markdown("### 💰 Totales del Inventario")
        st.caption(f"💱 Tipo de cambio utilizado: ${tipo_cambio:,.0f} ARS/USD")
        
        # KPIs Reorganizados - Sin Repeticiones
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Total de venta en USD
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${totals['total_venta_usd']:,.2f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Total Venta (USD)</p>
                <small style="color: #999;">Valor total de venta</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Total de venta en ARS
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${totals['total_venta_pesos']:,.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Total Venta (ARS)</p>
                <small style="color: #999;">Valor total de venta en pesos</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Costo base total en USD
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${totals['total_costo_base_usd']:,.2f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Costo Base Total (USD)</p>
                <small style="color: #999;">Costo base sin impuestos</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Costo base total en ARS
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${totals['total_costo_base_pesos']:,.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Costo Base Total (ARS)</p>
                <small style="color: #999;">Costo base en pesos</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Segunda fila de KPIs - Ganancias y Margen juntos
        st.markdown("")
        col5, col6, col7 = st.columns(3)
        
        with col5:
            # Ganancia real total en USD
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${totals['total_ganancia_real_usd']:,.2f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Ganancia Real Total (USD)</p>
                <small style="color: #999;">Venta - valuación real</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            # Ganancia real total en ARS
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${totals['total_ganancia_real_pesos']:,.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Ganancia Real Total (ARS)</p>
                <small style="color: #999;">Ganancia total en pesos</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col7:
            # Margen real
            margen_real_pct = (totals['total_ganancia_real_usd'] / totals['total_valuacion_real_usd'] * 100) if totals['total_valuacion_real_usd'] > 0 else 0
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">{margen_real_pct:.1f}%</h3>
                <p style="margin: 0; color: #666;">Margen Real (%)</p>
                <small style="color: #999;">Ganancia real / Valuación real</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Tercera fila - KPIs específicos para venta al mayor
        st.markdown("")
        st.markdown("### 🏪 KPIs Venta al Mayor")
        
        # Calcular totales para venta al mayor
        if 'precio_mayor_unitario' in df_processed.columns:
            total_venta_mayor_usd = df_processed['valor_venta_mayor_usd'].sum()
            total_venta_mayor_pesos = df_processed['valor_venta_mayor_pesos'].sum()
            total_ganancia_mayor_usd = df_processed['ganancia_mayor_usd'].sum()
            total_ganancia_mayor_pesos = df_processed['ganancia_mayor_pesos'].sum()
            
            # Calcular margen promedio al mayor
            if total_venta_mayor_usd > 0:
                margen_mayor_pct = (total_ganancia_mayor_usd / totals['total_valuacion_real_usd']) * 100
            else:
                margen_mayor_pct = 0
        else:
            total_venta_mayor_usd = 0
            total_venta_mayor_pesos = 0
            total_ganancia_mayor_usd = 0
            total_ganancia_mayor_pesos = 0
            margen_mayor_pct = 0
        
        col_mayor1, col_mayor2, col_mayor3, col_mayor4 = st.columns(4)
        
        with col_mayor1:
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${total_venta_mayor_usd:,.2f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Venta Total Mayor (USD)</p>
                <small style="color: #999;">Si vendes todo al mayor</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_mayor2:
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${total_venta_mayor_pesos:,.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Venta Total Mayor (ARS)</p>
                <small style="color: #999;">Valor total en pesos</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_mayor3:
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${total_ganancia_mayor_usd:,.2f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Ganancia Mayor (USD)</p>
                <small style="color: #999;">Ganancia si vendes al mayor</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_mayor4:
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">{margen_mayor_pct:.1f}%</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Margen Mayor (%)</p>
                <small style="color: #999;">Margen promedio al mayor</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Cuarta fila - KPIs de Publicidad y Tiempo de Venta
        st.markdown("")
        st.markdown("### 📢 Estrategia de Publicidad y Venta")
        
        # Calcular presupuesto total de publicidad
        if 'precio_mayor_unitario' in df_processed.columns and 'precio_detal_unitario' in df_processed.columns:
            # Calcular diferencia total disponible para publicidad
            df_processed['diferencia_publicidad_usd'] = df_processed['precio_detal_unitario'] - df_processed['precio_mayor_unitario']
            df_processed['diferencia_publicidad_ars'] = df_processed['diferencia_publicidad_usd'] * tipo_cambio
            
            # Calcular presupuesto total multiplicando por el stock de cada producto
            df_processed['presupuesto_publicidad_producto_usd'] = df_processed['diferencia_publicidad_usd'] * df_processed['stock_actual']
            df_processed['presupuesto_publicidad_producto_ars'] = df_processed['diferencia_publicidad_ars'] * df_processed['stock_actual']
            
            presupuesto_total_publicidad_usd = df_processed['presupuesto_publicidad_producto_usd'].sum()
            presupuesto_total_publicidad_ars = df_processed['presupuesto_publicidad_producto_ars'].sum()
            
            # Calcular tiempo estimado de venta (asumiendo venta promedio de 10% del stock mensual)
            stock_total = df_processed['stock_actual'].sum()
            venta_mensual_estimada = stock_total * 0.10  # 10% del stock por mes
            meses_estimados = stock_total / venta_mensual_estimada if venta_mensual_estimada > 0 else 0
            
            # Calcular gasto mensual recomendado en publicidad
            gasto_mensual_recomendado_ars = presupuesto_total_publicidad_ars / meses_estimados if meses_estimados > 0 else 0
            
            # Calcular porcentaje del presupuesto total
            porcentaje_publicidad_total = (presupuesto_total_publicidad_ars / totals['total_venta_pesos']) * 100 if totals['total_venta_pesos'] > 0 else 0
        else:
            presupuesto_total_publicidad_usd = 0
            presupuesto_total_publicidad_ars = 0
            meses_estimados = 0
            gasto_mensual_recomendado_ars = 0
            porcentaje_publicidad_total = 0
        
        col_pub1, col_pub2, col_pub3, col_pub4 = st.columns(4)
        
        with col_pub1:
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${presupuesto_total_publicidad_ars:,.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Presupuesto Total Publicidad (ARS)</p>
                <small style="color: #999;">Diferencia detal vs mayor</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_pub2:
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">{meses_estimados:.1f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Meses Estimados de Venta</p>
                <small style="color: #999;">Basado en 10% mensual</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_pub3:
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">${gasto_mensual_recomendado_ars:,.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Gasto Mensual Recomendado (ARS)</p>
                <small style="color: #999;">Presupuesto / meses</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_pub4:
            st.markdown(f"""
            <div class="total-section">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">{porcentaje_publicidad_total:.1f}%</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">% Presupuesto del Total</p>
                <small style="color: #999;">Publicidad / Venta total</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Información adicional sobre la estrategia
        if presupuesto_total_publicidad_ars > 0:
            st.info(f"""
            💡 **Estrategia de Marketing Recomendada:**
            
            **📊 Presupuesto Total Disponible:** ${presupuesto_total_publicidad_ars:,.0f} ARS
            **⏱️ Tiempo Estimado de Venta:** {meses_estimados:.1f} meses (vendiendo 10% del stock mensual)
            **💰 Gasto Mensual Recomendado:** ${gasto_mensual_recomendado_ars:,.0f} ARS
            **📈 Porcentaje del Presupuesto:** {porcentaje_publicidad_total:.1f}% del valor total de venta
            
            **🎯 Recomendación:** Distribuye el presupuesto de manera uniforme durante los {meses_estimados:.1f} meses estimados para maximizar el retorno de inversión.
            """)
        
        # Exportar datos
        st.markdown("### 📤 Exportar Datos")
        
        # Crear Excel para descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_processed.to_excel(writer, sheet_name='Inventario', index=False)
            
            # Crear hoja de resumen
            resumen_data = {
                'Métrica': ['Total Productos', 'Costo Base Total (USD)', 'Impuestos Recuperables Total (USD)', 
                           'Valuación Real Total (USD)', 'Venta Total (USD)', 'Ganancia Real (USD)', 'Margen Real (%)'],
                'Valor': [totals['total_productos'], totals['total_costo_base_usd'], totals['total_impuestos_recuperables_usd'],
                         totals['total_valuacion_real_usd'], totals['total_venta_usd'], totals['total_ganancia_real_usd'],
                         f"{margen_real_pct:.1f}%"]
            }
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 Descargar Reporte Excel",
            data=output.getvalue(),
            file_name=f"inventario_valuacion_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        ) 