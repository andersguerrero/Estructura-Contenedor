import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

# Configuración de la página
st.set_page_config(
    page_title="Contenedor Completo",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
CONTAINER_40HQ_CBM = 70.0
PRODUCTOS_CSV = "productos_guardados.csv"
CONFIG_FILE = "container_config.json"

# Cache para cálculos pesados
# @st.cache_data(ttl=60)  # Cache deshabilitado temporalmente para debug
def calcular_dataframe_productos(productos, exolgan_puerto_usd, agencia_maritima_usd, almacenaje_usd, acarreo_usd, flete_cbm, precio_dolar, 
                                ddi_pct, tasas_pct, iva_pct, iva_adic_pct, ganancias_pct, iibb_pct, seguro_pct, agente_pct, despachante_pct):
    """Calcula el DataFrame optimizado de productos con todos los cálculos necesarios incluyendo impuestos"""
    if not productos:
        return pd.DataFrame()
    
    df = pd.DataFrame(productos)
    
    # Calcular totales una sola vez
    total_cbm = df['CBM Total'].sum()
    total_peso = df['Peso Total (kg)'].sum()
    
    # Convertir gastos fijos de USD a pesos según el tipo de cambio actual
    exolgan_puerto_pesos = exolgan_puerto_usd * precio_dolar
    agencia_maritima_pesos = agencia_maritima_usd * precio_dolar
    almacenaje_pesos = almacenaje_usd * precio_dolar
    acarreo_pesos = acarreo_usd * precio_dolar
    
    gastos_fijos_totales = exolgan_puerto_pesos + agencia_maritima_pesos + almacenaje_pesos + acarreo_pesos
    # CORRECCIÓN: Los gastos fijos se distribuyen por la capacidad del contenedor, no por el CBM cargado
    gastos_fijos_por_cbm = gastos_fijos_totales / CONTAINER_40HQ_CBM
    
    # Cálculos de gastos fijos y flete (distribuidos por CBM) - se calculan primero
    # CORRECCIÓN: Los gastos fijos se distribuyen por la capacidad del contenedor, no por el CBM cargado
    df['Exolgan Puerto por Producto (USD)'] = df['CBM Total'] * (exolgan_puerto_pesos / CONTAINER_40HQ_CBM) / precio_dolar
    df['Agencia Marítima por Producto (USD)'] = df['CBM Total'] * (agencia_maritima_pesos / CONTAINER_40HQ_CBM) / precio_dolar
    df['Almacenaje por Producto (USD)'] = df['CBM Total'] * (almacenaje_pesos / CONTAINER_40HQ_CBM) / precio_dolar
    df['Acarreo por Producto (USD)'] = df['CBM Total'] * (acarreo_pesos / CONTAINER_40HQ_CBM) / precio_dolar
    df['Flete por Producto (USD)'] = df['CBM Total'] * flete_cbm
    df['Gastos Fijos por Producto (USD)'] = df['CBM Total'] * gastos_fijos_por_cbm / precio_dolar
    
    # Cálculos base
    df['FOB (USD)'] = df['Precio FOB (USD)'] * df['Cantidad Total']
    df['Seguro (USD)'] = df['FOB (USD)'] * (seguro_pct / 100)
    
    # CIF = FOB + Seguro + Flete
    df['CIF (USD)'] = df['FOB (USD)'] + df['Seguro (USD)'] + df['Flete por Producto (USD)']
    
    # Usar DDI específico de cada producto, o el global si no existe
    if 'DDI (%)' not in df.columns:
        df['DDI (%)'] = ddi_pct
    else:
        # Asegurar que no haya valores nulos en DDI (%)
        df['DDI (%)'] = df['DDI (%)'].fillna(ddi_pct)
    df['DDI (USD)'] = df['CIF (USD)'] * (df['DDI (%)'] / 100)
    
    # Tasas Estadísticas sobre CIF
    df['Tasas (USD)'] = df['CIF (USD)'] * (tasas_pct / 100)
    
    # VALOR IVA = CIF + DDI + Tasas Estadísticas
    df['Valor IVA (USD)'] = df['CIF (USD)'] + df['DDI (USD)'] + df['Tasas (USD)']
    
    # Impuestos sobre VALOR IVA
    df['IVA (USD)'] = df['Valor IVA (USD)'] * (iva_pct / 100)
    df['IVA Adicional (USD)'] = df['Valor IVA (USD)'] * (iva_adic_pct / 100)
    df['Ganancias (USD)'] = df['Valor IVA (USD)'] * (ganancias_pct / 100)
    df['IIBB (USD)'] = df['Valor IVA (USD)'] * (iibb_pct / 100)
    
    # Otros gastos sobre FOB
    df['Agente (USD)'] = df['FOB (USD)'] * (agente_pct / 100)
    df['Despachante (USD)'] = df['FOB (USD)'] * (despachante_pct / 100)
    
    # Antidumping (campo específico por producto)
    if 'Antidumping (USD)' in df.columns:
        df['Antidumping (USD)'] = df['Antidumping (USD)'].fillna(0)
    else:
        df['Antidumping (USD)'] = 0
    
    # Asegurar que todos los campos numéricos tengan valores válidos
    campos_numericos = ['Precio FOB (USD)', 'Cantidad Total', 'CBM Total', 'Peso Total (kg)']
    for campo in campos_numericos:
        if campo in df.columns:
            df[campo] = df[campo].fillna(0)
    
    # Costo base (solo costos básicos de importación)
    df['Costo Base (USD)'] = (df['CIF (USD)'] + df['DDI (USD)'] + df['Tasas (USD)'] + df['Antidumping (USD)'])
    
    # Costo total SIN impuestos recuperables (solo costos no recuperables)
    df['Costo sin Impuestos Recuperables (USD)'] = (df['CIF (USD)'] + df['DDI (USD)'] + df['Tasas (USD)'] + 
                                                   df['Antidumping (USD)'] + df['Agente (USD)'] + df['Despachante (USD)'])
    
    # Costo total CON impuestos recuperables (para referencia de caja)
    df['Costo con Impuestos Recuperables (USD)'] = (df['CIF (USD)'] + df['DDI (USD)'] + df['Tasas (USD)'] + 
                                                   df['Antidumping (USD)'] + df['Ganancias (USD)'] + df['IIBB (USD)'] + 
                                                   df['Agente (USD)'] + df['Despachante (USD)'])
    
    # Costo final para precio del producto (SIN impuestos recuperables)
    df['Costo Adicional por Producto (USD)'] = df['Gastos Fijos por Producto (USD)']
    df['Costo Final por Producto (USD)'] = df['Costo sin Impuestos Recuperables (USD)'] + df['Costo Adicional por Producto (USD)']
    
    # Calcular precio unitario final con validación
    df['Precio Unitario Final (USD)'] = df['Costo Final por Producto (USD)'] / df['Cantidad Total'].replace(0, 1)  # Evitar división por cero
    df['Precio Unitario Final (Pesos)'] = df['Precio Unitario Final (USD)'] * precio_dolar
    
    # Validar que no haya valores infinitos o NaN
    df = df.replace([np.inf, -np.inf], 0)
    df = df.fillna(0)
    
    # Calcular Precio Estimado de Venta
    # Fórmula: Precio de Venta ARS + 100% ganancia + 21% IVA + 15% MercadoLibre + Comisión por rango
    precio_base = df['Precio Unitario Final (Pesos)']
    ganancia_100 = precio_base * 1.0  # 100% de ganancia
    subtotal_con_ganancia = precio_base + ganancia_100
    iva_21 = subtotal_con_ganancia * 0.21  # 21% de IVA
    subtotal_con_iva = subtotal_con_ganancia + iva_21
    mercadolibre_15 = subtotal_con_iva * 0.15  # 15% de MercadoLibre
    precio_sin_comision = subtotal_con_iva + mercadolibre_15
    
    # Calcular comisión adicional por rango de precio
    def calcular_comision_adicional(precio):
        if precio <= 15000:
            return 1095
        elif precio <= 25000:
            return 2190
        elif precio <= 33000:
            return 2628
        else:
            return 0
    
    # Aplicar comisión condicional
    comision_adicional = precio_sin_comision.apply(calcular_comision_adicional)
    precio_estimado_venta = precio_sin_comision + comision_adicional
    
    df['Precio MercadoLibre (ARS)'] = precio_estimado_venta
    df['Comisión Adicional (ARS)'] = comision_adicional
    
    # Calcular CBM por producto individual
    df['CBM por Producto'] = df['CBM Total'] / df['Cantidad Total'].replace(0, 1)
    
    # Debug: Verificar si hay productos con precios en $0
    productos_con_precio_cero = df[df['Precio Unitario Final (USD)'] == 0]
    if not productos_con_precio_cero.empty:
        st.warning(f"⚠️ **Atención:** {len(productos_con_precio_cero)} producto(s) tienen precio final en $0. Verifica los datos de entrada.")
        for idx, row in productos_con_precio_cero.iterrows():
            st.info(f"🔍 Producto '{row['Nombre']}': FOB=${row['Precio FOB (USD)']:.2f}, Cantidad={row['Cantidad Total']}, CBM={row['CBM Total']:.4f}")
    
    # Porcentajes de distribución proporcional (basados en la capacidad del contenedor)
    df['% del CBM del Contenedor'] = (df['CBM Total'] / CONTAINER_40HQ_CBM * 100).round(2)
    df['% del CBM Utilizado'] = (df['CBM Total'] / total_cbm * 100).round(2) if total_cbm > 0 else 0
    df['% del Peso'] = (df['Peso Total (kg)'] / total_peso * 100).round(2)
    df['% del Costo'] = (df['Costo Final por Producto (USD)'] / df['Costo Final por Producto (USD)'].sum() * 100).round(2)
    
    # Verificación de proporcionalidad (basada en el CBM utilizado)
    df['Verificación Gastos Fijos (%)'] = (df['Gastos Fijos por Producto (USD)'] / df['Gastos Fijos por Producto (USD)'].sum() * 100).round(2)
    df['Verificación Flete (%)'] = (df['Flete por Producto (USD)'] / df['Flete por Producto (USD)'].sum() * 100).round(2)
    
    return df, total_cbm, total_peso, gastos_fijos_totales, gastos_fijos_por_cbm

def verificar_proporcionalidad(df):
    """Verifica que la distribución de costos sea proporcional"""
    verificaciones = {}
    
    # Verificar que los porcentajes sumen 100%
    total_cbm_utilizado_pct = df['% del CBM Utilizado'].sum()
    total_peso_pct = df['% del Peso'].sum()
    total_gastos_fijos_pct = df['Verificación Gastos Fijos (%)'].sum()
    total_flete_pct = df['Verificación Flete (%)'].sum()
    
    verificaciones['CBM Utilizado'] = abs(total_cbm_utilizado_pct - 100) < 0.01
    verificaciones['Peso'] = abs(total_peso_pct - 100) < 0.01
    verificaciones['Gastos Fijos'] = abs(total_gastos_fijos_pct - 100) < 0.01
    verificaciones['Flete'] = abs(total_flete_pct - 100) < 0.01
    
    # Verificar que los gastos fijos sean proporcionales al CBM utilizado
    gastos_fijos_proporcionales = True
    for idx, row in df.iterrows():
        cbm_pct = row['% del CBM Utilizado']
        gastos_fijos_pct = row['Verificación Gastos Fijos (%)']
        if abs(cbm_pct - gastos_fijos_pct) > 0.01:
            gastos_fijos_proporcionales = False
            break
    
    verificaciones['Gastos Fijos Proporcionales'] = gastos_fijos_proporcionales
    
    # Verificar utilización del contenedor
    total_cbm_cargado = df['CBM Total'].sum()
    utilizacion_contenedor = (total_cbm_cargado / CONTAINER_40HQ_CBM * 100).round(2)
    verificaciones['Utilización Contenedor'] = utilizacion_contenedor <= 100
    
    return verificaciones

# Utilidades para cargar y guardar configuración de gastos fijos
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

# Utilidad para guardar productos
def guardar_productos_csv(df_calculado=None):
    try:
        if df_calculado is not None:
            # Guardar el DataFrame calculado con todos los costos
            df_calculado.to_csv(PRODUCTOS_CSV, index=False)
        elif 'productos' in st.session_state and st.session_state['productos']:
            df = pd.DataFrame(st.session_state['productos'])
            df.to_csv(PRODUCTOS_CSV, index=False)
        
            # Verificar que se guardó correctamente
            if os.path.exists(PRODUCTOS_CSV):
                return True
            else:
                return False
    except Exception as e:
        st.error(f"Error al guardar productos: {e}")
        return False



# Cargar productos guardados con mejor manejo de errores
if 'productos' not in st.session_state:
    st.session_state['productos'] = []

# FORZAR CARGA DESDE CSV - Solución robusta para el problema de persistencia
try:
    if os.path.exists(PRODUCTOS_CSV):
        df_csv = pd.read_csv(PRODUCTOS_CSV)
        if not df_csv.empty:
            # Siempre cargar desde CSV para mantener consistencia
            st.session_state['productos'] = df_csv.to_dict('records')
            
            # Cargar configuración de antidumping si existe
            config = load_config()
            if 'antidumping' in config:
                antidumping_config = config['antidumping']
                for prod in st.session_state['productos']:
                    nombre = prod.get('Nombre', '')
                    if nombre in antidumping_config:
                        prod['Antidumping (USD)'] = antidumping_config[nombre]
        else:
            st.warning("⚠️ El archivo CSV está vacío")
    else:
        st.info("ℹ️ No hay productos cargados. Carga productos desde el módulo de inicio.")
except Exception as e:
    st.error(f"❌ Error cargando productos desde CSV: {e}")
    if not st.session_state['productos']:
        st.session_state['productos'] = []

# CSS personalizado mejorado
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1d391kg {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Variables CSS para colores de MercadoLibre */
    :root {
        --ml-yellow: #FFE600;
        --ml-yellow-dark: #E6CF00;
        --ml-yellow-light: #FFF533;
        --ml-blue: #3483FA;
        --ml-blue-dark: #2968CC;
        --ml-blue-light: #5B9AFF;
        --ml-gray-dark: #333333;
        --ml-gray-medium: #666666;
        --ml-gray-light: #999999;
        --ml-gray-very-light: #EEEEEE;
        --ml-white: #FFFFFF;
        --ml-black: #000000;
        --ml-green: #39B54A;
        --ml-red: #E74C3C;
        --ml-orange: #FF6B35;
        
        /* Variables derivadas */
        --primary-color: var(--ml-yellow);
        --primary-dark: var(--ml-yellow-dark);
        --primary-light: var(--ml-yellow-light);
        --secondary-color: var(--ml-blue);
        --accent-color: var(--ml-orange);
        --success-color: var(--ml-green);
        --warning-color: var(--ml-orange);
        --error-color: var(--ml-red);
        --background-light: var(--ml-gray-very-light);
        --background-white: var(--ml-white);
        --background-gradient: linear-gradient(135deg, var(--ml-yellow) 0%, var(--ml-yellow-light) 100%);
        --background-gradient-blue: linear-gradient(135deg, var(--ml-blue) 0%, var(--ml-blue-light) 100%);
        --text-primary: var(--ml-gray-dark);
        --text-secondary: var(--ml-gray-medium);
        --border-color: #DDDDDD;
        --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        --border-radius: 12px;
        --border-radius-lg: 16px;
        --border-radius-xl: 20px;
        --text-dark: var(--ml-gray-dark);
        --text-light: var(--ml-gray-medium);
        --bg-light: var(--ml-gray-very-light);
    }
    
    /* Estilos generales */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Contenedores de sección */
    .section-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .section-container:hover {
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Títulos de sección */
    .section-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, #FFF533 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 5px 15px rgba(255, 230, 0, 0.2);
    }
    
    .section-header h2 {
        color: var(--text-dark);
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Tarjetas de resultados */
    .result-card {
        background: linear-gradient(135deg, #ffffff 0%, var(--bg-light) 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .result-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .result-card .result-label {
        font-size: 0.9rem;
        color: var(--text-light);
        margin-bottom: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .result-card .result-value {
        font-size: 1.8rem;
        font-weight: 900;
        color: var(--text-dark);
        margin-bottom: 0.3rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* KPIs con gradientes */
    .kpi-header {
        background: linear-gradient(135deg, var(--secondary-color) 0%, var(--accent-color) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .kpi-header h3 {
        color: white;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .kpi-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: var(--background-gradient);
        color: var(--ml-gray-dark);
        border: 2px solid var(--ml-yellow-dark);
        border-radius: var(--border-radius);
        font-weight: 700;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
        background: linear-gradient(135deg, var(--ml-yellow-light) 0%, var(--ml-yellow) 100%);
        border-color: var(--ml-yellow-dark);
    }
    
    /* Dataframes mejorados */
    .stDataFrame {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
    }
    
    /* Métricas mejoradas */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, var(--bg-light) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    /* Sidebar mejorado */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Expander mejorado */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--primary-color) 0%, #FFF533 100%) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: var(--text-dark) !important;
    }
    
    /* Mensajes de éxito/error mejorados */
    .stSuccess {
        background: linear-gradient(135deg, var(--success-color) 0%, #059669 100%) !important;
        border-radius: 10px !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, var(--danger-color) 0%, #dc2626 100%) !important;
        border-radius: 10px !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Animaciones */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .section-container {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .section-header h2 {
            font-size: 1.4rem;
        }
        
        .result-card .result-value {
            font-size: 1.4rem;
        }
    }
    
    /* Efectos adicionales */
    .stButton > button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
    }
    
    /* Mejoras para métricas */
    .stMetric > div {
        border-radius: 15px !important;
        padding: 1rem !important;
        background: linear-gradient(135deg, #ffffff 0%, var(--bg-light) 100%) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08) !important;
        border: 1px solid var(--border-color) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric > div:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12) !important;
    }
    
    /* Mejoras para el sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    /* Mejoras para expanders */
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #FFF533 0%, var(--primary-color) 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 230, 0, 0.2) !important;
    }
    
    /* Animación de carga */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Navegación moderna con botones funcionales
st.markdown("### 🧭 Navegación")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🏠 Inicio", key="nav-home", use_container_width=True):
        st.switch_page("app_costos_final.py")
with col2:
    if st.button("📦 Contenedor", key="nav-container", use_container_width=True, type="primary"):
        st.switch_page("pages/contenedor_completo.py")
with col3:
    if st.button("💰 Ganancias", key="nav-calculator", use_container_width=True):
        st.switch_page("pages/precio_venta.py")
with col4:
    if st.button("📋 Inventario", key="nav-inventory", use_container_width=True):
        st.switch_page("pages/inventario.py")
with col5:
    if st.button("🚀 ML Pro", key="nav-precio-ml-pro", use_container_width=True):
        st.switch_page("pages/precio_venta_ml_avanzado.py")

st.markdown("---")

# Sección de instrucciones
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(255, 230, 0, 0.1) 0%, rgba(255, 245, 51, 0.1) 100%); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border: 1px solid rgba(255, 230, 0, 0.3);">
    <p style="color: var(--text-dark); font-size: 1rem; margin: 0; font-weight: 500;">
    💡 <strong>Tip:</strong> Los gastos fijos se distribuyen proporcionalmente por CBM entre todos los productos del contenedor.
</p>
</div>
""", unsafe_allow_html=True)

# Cargar configuración guardada
config = load_config()

# Sidebar para configuración
with st.sidebar:
    st.markdown("### 🚢 Flete")
    st.markdown("*Aplicado por CBM de cada producto*")
    
    flete_cbm = st.number_input(
        "Flete por CBM (USD)",
        min_value=0.0,
        value=float(config.get('flete_cbm', 93.0)),
        step=1.0,
        format="%.2f",
        help="Flete por metro cúbico en USD"
    )
    
    st.markdown("### 💰 Gastos Fijos del Contenedor (USD)")
    st.markdown("*Valores originales en USD (tasa base: $1,100 pesos/USD)*")
    
    # Tasa de cambio base utilizada para calcular los valores originales
    TASA_BASE = 1100.0  # pesos por dólar
    
    # Manejar tanto valores antiguos en pesos como nuevos en USD
    # Valores nuevos en USD (preferidos)
    exolgan_usd_base = config.get('exolgan_puerto_usd', 0)
    agencia_usd_base = config.get('agencia_maritima_usd', 0)
    almacenaje_usd_base = config.get('almacenaje_usd', 0)
    acarreo_usd_base = config.get('acarreo_usd', 0)
    
    # Si no hay valores en USD, convertir los valores antiguos en pesos
    if exolgan_usd_base == 0:
        exolgan_value = config.get('exolgan_puerto', config.get('exlogan_puerto', 0))
        exolgan_usd_base = exolgan_value / TASA_BASE if exolgan_value > 0 else 0
    
    if agencia_usd_base == 0:
        agencia_value = config.get('agencia_maritima', 0)
        agencia_usd_base = agencia_value / TASA_BASE
    
    if almacenaje_usd_base == 0:
        almacenaje_value = config.get('almacenaje', 0)
        almacenaje_usd_base = almacenaje_value / TASA_BASE
    
    if acarreo_usd_base == 0:
        acarreo_value = config.get('acarreo', 0)
        acarreo_usd_base = acarreo_value / TASA_BASE
    
    exolgan_puerto_usd = st.number_input(
        "Exolgan Puerto (USD)",
        min_value=0.0,
        value=float(exolgan_usd_base),
        step=100.0,
        format="%.2f",
        help="Gastos de exolgan en puerto en USD"
    )
    
    agencia_maritima_usd = st.number_input(
        "Agencia Marítima (USD)",
        min_value=0.0,
        value=float(agencia_usd_base),
        step=100.0,
        format="%.2f",
        help="Gastos de agencia marítima en USD"
    )
    
    almacenaje_usd = st.number_input(
        "Almacenaje (USD)",
        min_value=0.0,
        value=float(almacenaje_usd_base),
        step=100.0,
        format="%.2f",
        help="Gastos de almacenaje en USD"
    )
    
    acarreo_usd = st.number_input(
        "Acarreo (USD)",
        min_value=0.0,
        value=float(acarreo_usd_base),
        step=100.0,
        format="%.2f",
        help="Gastos de acarreo en USD"
    )
    
    # Calcular total de gastos fijos en USD
    gastos_fijos_total_usd = exolgan_puerto_usd + agencia_maritima_usd + almacenaje_usd + acarreo_usd
    
    # Mostrar resumen de gastos fijos
    st.markdown(f"**💰 Total Gastos Fijos: ${gastos_fijos_total_usd:,.2f} USD**")
    
    # Mostrar valores equivalentes en pesos según el tipo de cambio actual
    precio_dolar_actual = st.session_state.get('precio_dolar', 1250.0)
    
    # Cargar valor del archivo de configuración si existe
    try:
        if os.path.exists('container_config.json'):
            with open('container_config.json', 'r') as f:
                config = json.load(f)
                if 'precio_dolar' in config:
                    precio_dolar_actual = config['precio_dolar']
                    st.session_state['precio_dolar'] = precio_dolar_actual
    except:
        pass
    
    precio_dolar_edit = st.number_input(
        "Tipo de cambio USD → ARS",
        min_value=1.0,
        value=float(precio_dolar_actual),  # Usar session_state como prioridad
        step=10.0,
        format="%.0f",
        key="precio_dolar_container",
        help="Valor del dólar en pesos argentinos"
    )
    
    # Actualizar session_state si cambió el valor
    if precio_dolar_edit != precio_dolar_actual:
        st.session_state['precio_dolar'] = precio_dolar_edit
        # Guardar en archivo de configuración
        config = {}
        try:
            if os.path.exists('container_config.json'):
                with open('container_config.json', 'r') as f:
                    config = json.load(f)
        except:
            config = {}
        
        config['precio_dolar'] = precio_dolar_edit
        with open('container_config.json', 'w') as f:
            json.dump(config, f)
        
        st.success(f"✅ Tipo de cambio actualizado: ${precio_dolar_edit:,.0f} pesos/USD")
    
    # Calcular valores en pesos según el tipo de cambio actual
    exolgan_pesos_actual = exolgan_puerto_usd * precio_dolar_edit
    agencia_pesos_actual = agencia_maritima_usd * precio_dolar_edit
    almacenaje_pesos_actual = almacenaje_usd * precio_dolar_edit
    acarreo_pesos_actual = acarreo_usd * precio_dolar_edit
    gastos_fijos_total_pesos = gastos_fijos_total_usd * precio_dolar_edit
    
    # Mostrar valores equivalentes en pesos
    st.markdown("**📊 Valores equivalentes en pesos (según tipo de cambio actual):**")
    st.markdown(f"• Exolgan Puerto: ${exolgan_pesos_actual:,.0f} pesos")
    st.markdown(f"• Agencia Marítima: ${agencia_pesos_actual:,.0f} pesos")
    st.markdown(f"• Almacenaje: ${almacenaje_pesos_actual:,.0f} pesos")
    st.markdown(f"• Acarreo: ${acarreo_pesos_actual:,.0f} pesos")
    st.markdown(f"**💰 Total: ${gastos_fijos_total_pesos:,.0f} pesos**")
    
    st.markdown("### 💱 Tipo de Cambio")
    st.markdown("*Para conversiones USD → ARS*")
    
    # Asegurar que el precio del dólar esté inicializado correctamente
    if 'precio_dolar' not in st.session_state:
        st.session_state['precio_dolar'] = precio_dolar_edit
    elif precio_dolar_edit != st.session_state.get('precio_dolar'):
        # Si el valor del input es diferente al session_state, actualizar
        st.session_state['precio_dolar'] = precio_dolar_edit
    
    # Obtener valores de impuestos del session_state (ocultos del sidebar)
    ddi_pct = st.session_state.get('ddi_pct', 18.0)
    tasas_pct = st.session_state.get('tasas_pct', 3.0)
    iva_pct = st.session_state.get('iva_pct', 21.0)
    iva_adic_pct = st.session_state.get('iva_adic_pct', 20.0)
    ganancias_pct = st.session_state.get('ganancias_pct', 6.0)
    iibb_pct = st.session_state.get('iibb_pct', 2.0)
    seguro_pct = st.session_state.get('seguro_pct', 0.5)
    agente_pct = st.session_state.get('agente_pct', 4.0)
    despachante_pct = st.session_state.get('despachante_pct', 1.0)

    # --- Configuración de Antidumping por Producto ---
    st.markdown("---")
    
    # Contar productos con antidumping
    productos_con_antidumping = 0
    total_antidumping = 0.0
    if 'productos' in st.session_state and st.session_state['productos']:
        for prod in st.session_state['productos']:
            valor = float(prod.get('Antidumping (USD)', 0.0))
            if valor > 0:
                productos_con_antidumping += 1
                total_antidumping += valor
    
    # Mostrar resumen compacto
    if productos_con_antidumping > 0:
        st.markdown(f"**🛡️ Antidumping:** {productos_con_antidumping} productos (${total_antidumping:,.2f} USD)")
    else:
        st.markdown("**🛡️ Antidumping:** Sin productos asignados")
    
    # Expander para gestionar antidumping
    with st.expander("✏️ Gestionar Antidumping", expanded=False):
        st.markdown("*Asignar y editar montos de antidumping*")
        
        if 'productos' in st.session_state and st.session_state['productos']:
            # Mostrar todos los productos con sus valores de antidumping
            st.markdown("**📋 Productos y sus valores de antidumping:**")
            
            for i, prod in enumerate(st.session_state['productos']):
                nombre_producto = prod.get('Nombre', f'Producto {i+1}')
                valor_actual = float(prod.get('Antidumping (USD)', 0.0))
                
                # Crear columnas para cada producto
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{nombre_producto}**")
                
                with col2:
                    if valor_actual > 0:
                        st.write(f"${valor_actual:,.2f} USD")
                    else:
                        st.write("$0.00 USD")
                
                with col3:
                    # Botón de editar
                    if st.button("✏️", key=f"edit_{i}", help=f"Editar antidumping de {nombre_producto}"):
                        st.session_state[f'editing_{i}'] = True
                
                # Campo de edición (aparece solo cuando se presiona editar)
                if st.session_state.get(f'editing_{i}', False):
                    nuevo_valor = st.number_input(
                        f"Nuevo valor para {nombre_producto}:",
                        min_value=0.0,
                        value=valor_actual,
                        step=0.01,
                        format="%.2f",
                        key=f"edit_input_{i}"
                    )

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Guardar", key=f"save_{i}"):
                            st.session_state['productos'][i]['Antidumping (USD)'] = nuevo_valor
                            # Guardar en configuración
                            config = load_config()
                            if 'antidumping' not in config:
                                config['antidumping'] = {}
                            config['antidumping'][nombre_producto] = nuevo_valor
                            save_config(config)
                            guardar_productos_csv()
                            st.session_state[f'editing_{i}'] = False
                            st.success(f"✅ Actualizado: ${nuevo_valor:,.2f} USD")
                            st.rerun()

                    with col_cancel:
                        if st.button("❌ Cancelar", key=f"cancel_{i}"):
                            st.session_state[f'editing_{i}'] = False
                            st.rerun()
            
            # Botón para limpiar todos los antidumpings
            st.markdown("---")
            if st.button("🗑️ Limpiar TODOS los Antidumpings", type="secondary", use_container_width=True,
                        help="Elimina el antidumping de todos los productos"):
                for prod in st.session_state['productos']:
                    prod['Antidumping (USD)'] = 0.0
                # Limpiar configuración guardada
                config = load_config()
                if 'antidumping' in config:
                    del config['antidumping']
                    save_config(config)
                st.success("✅ Todos los antidumpings han sido eliminados")
                st.rerun()
        else:
            st.info("ℹ️ Agrega productos desde el análisis individual para configurar antidumping.")

    # Botón para guardar configuración
    st.markdown("---")
    if st.button("💾 Guardar Configuración", type="primary", use_container_width=True):
        try:
            # Guardar configuración de gastos fijos
            config = {
                'exolgan_puerto_usd': exolgan_puerto_usd,
                'agencia_maritima_usd': agencia_maritima_usd,
                'almacenaje_usd': almacenaje_usd,
                'acarreo_usd': acarreo_usd,
                'flete_cbm': flete_cbm,
                'precio_dolar': precio_dolar_edit
            }
            
            # Guardar configuración de antidumping
            if 'productos' in st.session_state and st.session_state['productos']:
                antidumping_config = {}
                for prod in st.session_state['productos']:
                    nombre = prod.get('Nombre', '')
                    antidumping_valor = float(prod.get('Antidumping (USD)', 0.0))
                    if antidumping_valor > 0:
                        antidumping_config[nombre] = antidumping_valor
                
                if antidumping_config:
                    config['antidumping'] = antidumping_config
            
            # Guardar productos actualizados
                guardar_productos_csv()
            
            save_config(config)
            st.success("✅ Configuración y productos guardados correctamente")
        except Exception as e:
            st.error(f"❌ Error al guardar la configuración: {e}")

# Lógica principal
# Verificar si los datos se perdieron y forzar recarga si es necesario
if len(st.session_state['productos']) == 0 and os.path.exists(PRODUCTOS_CSV):
    try:
        df_csv = pd.read_csv(PRODUCTOS_CSV)
        if not df_csv.empty:
            st.session_state['productos'] = df_csv.to_dict('records')
            st.info("🔄 Datos recuperados automáticamente desde CSV")
    except Exception as e:
        st.error(f"❌ Error recuperando datos: {e}")

if len(st.session_state['productos']) > 0:
    # Usar el precio del dólar del session_state para asegurar consistencia
    precio_dolar = st.session_state.get('precio_dolar', precio_dolar_edit)
    
    # Calcular DataFrame optimizado una sola vez
    df_productos, total_cbm, total_peso, gastos_fijos_totales, gastos_fijos_por_cbm = calcular_dataframe_productos(
        st.session_state['productos'], exolgan_puerto_usd, agencia_maritima_usd, almacenaje_usd, acarreo_usd, flete_cbm, precio_dolar,
        ddi_pct, tasas_pct, iva_pct, iva_adic_pct, ganancias_pct, iibb_pct, seguro_pct, agente_pct, despachante_pct
    )
    
    # Guardar el DataFrame calculado en session_state para que otros módulos puedan acceder
    st.session_state['df_productos_calculado'] = df_productos.copy()
    

    
    # Calcular totales adicionales
    total_costo_base_usd = df_productos['Costo Base (USD)'].sum()
    
    # Verificar que las columnas existen antes de calcular
    if 'Costo sin Impuestos Recuperables (USD)' not in df_productos.columns:
        st.error("❌ Error: La columna 'Costo sin Impuestos Recuperables (USD)' no existe en el DataFrame")
        st.write("Columnas disponibles:", list(df_productos.columns))
        st.stop()
    
    if 'Costo con Impuestos Recuperables (USD)' not in df_productos.columns:
        st.error("❌ Error: La columna 'Costo con Impuestos Recuperables (USD)' no existe en el DataFrame")
        st.write("Columnas disponibles:", list(df_productos.columns))
        st.stop()
    
    total_costo_sin_recuperables_usd = df_productos['Costo sin Impuestos Recuperables (USD)'].sum()
    total_costo_con_recuperables_usd = df_productos['Costo con Impuestos Recuperables (USD)'].sum()
    total_iva_usd = df_productos['IVA (USD)'].sum()
    total_iva_adic_usd = df_productos['IVA Adicional (USD)'].sum()
    total_ganancias_usd = df_productos['Ganancias (USD)'].sum()
    total_iibb_usd = df_productos['IIBB (USD)'].sum()
    total_agente_usd = df_productos['Agente (USD)'].sum()
    total_despachante_usd = df_productos['Despachante (USD)'].sum()
    total_seguro_usd = df_productos['Seguro (USD)'].sum()
    total_ddi_usd = df_productos['DDI (USD)'].sum()
    total_tasas_usd = df_productos['Tasas (USD)'].sum()
    total_antidumping_usd = df_productos['Antidumping (USD)'].sum()
    flete_total_usd = total_cbm * flete_cbm
    gastos_fijos_total_usd = gastos_fijos_totales / precio_dolar
    # Costo total completo incluyendo TODOS los costos (inversión real total)
    # NOTA: total_costo_con_recuperables_usd ya incluye el flete (está en CIF)
    total_costo_usd = (total_costo_con_recuperables_usd + 
                      total_iva_usd + 
                      total_iva_adic_usd + 
                      gastos_fijos_total_usd)
    total_costo_pesos = total_costo_usd * precio_dolar
    contenedores_necesarios_total = total_cbm / CONTAINER_40HQ_CBM
    
    # Calcular utilización del contenedor
    total_cbm_cargado = df_productos['CBM Total'].sum()
    utilizacion_contenedor = (total_cbm_cargado / CONTAINER_40HQ_CBM * 100).round(2)
    espacio_disponible = CONTAINER_40HQ_CBM - total_cbm_cargado
    
    # Mostrar resumen general unificado
    st.markdown("""
<div class="section-header">
    <h2>📊 Resumen General del Contenedor</h2>
</div>
""",
        unsafe_allow_html=True
    )
    
    # KPIs principales con diseño mejorado
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Total CBM</div>
            <div class="result-value">{total_cbm:.2f}</div>
            <div class="result-label">m³</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">📊 Espacio Disponible</div>
            <div class="result-value">{espacio_disponible:.2f}</div>
            <div class="result-label">m³ ({(100-utilizacion_contenedor):.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Total Peso</div>
            <div class="result-value">{total_peso:,.0f}</div>
            <div class="result-label">kg</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Costo Total USD</div>
            <div class="result-value">${total_costo_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    


    # Mostrar tabla de productos mejorada
    st.markdown(
        """
<div class="section-header">
    <h2>📋 Análisis por Producto</h2>
</div>
""",
        unsafe_allow_html=True
    )

    # Crear DataFrame simplificado para la tabla con manejo de valores nulos
    try:
        # Verificar que las columnas necesarias existen
        required_columns = ['Nombre', 'Precio Unitario Final (Pesos)', 'Cantidad Total', 'Precio Unitario Final (USD)', 'CBM Total']
        missing_columns = [col for col in required_columns if col not in df_productos.columns]
        
        if missing_columns:
            st.error(f"❌ Faltan las siguientes columnas en el DataFrame: {', '.join(missing_columns)}")
            st.info("💡 Esto puede indicar un problema en el cálculo de productos")
            st.stop()
        
        # Crear DataFrame con las columnas requeridas
        df_display = df_productos[required_columns].copy()
        
        # Manejar valores nulos
        df_display['Precio Unitario Final (Pesos)'] = df_display['Precio Unitario Final (Pesos)'].fillna(0)
        df_display['Cantidad Total'] = df_display['Cantidad Total'].fillna(0)
        df_display['Precio Unitario Final (USD)'] = df_display['Precio Unitario Final (USD)'].fillna(0)
        df_display['CBM Total'] = df_display['CBM Total'].fillna(0)
        df_display['Nombre'] = df_display['Nombre'].fillna('Sin nombre')
        
        # Calcular Precio Estimado de Venta
        # Fórmula: Precio de Venta ARS + 100% ganancia + 21% IVA + 15% MercadoLibre + Comisión por rango
        precio_base = df_display['Precio Unitario Final (Pesos)']
        ganancia_100 = precio_base * 1.0  # 100% de ganancia
        subtotal_con_ganancia = precio_base + ganancia_100
        iva_21 = subtotal_con_ganancia * 0.21  # 21% de IVA
        subtotal_con_iva = subtotal_con_ganancia + iva_21
        mercadolibre_15 = subtotal_con_iva * 0.15  # 15% de MercadoLibre
        precio_sin_comision = subtotal_con_iva + mercadolibre_15
        
        # Calcular comisión adicional por rango de precio
        def calcular_comision_adicional(precio):
            if precio <= 15000:
                return 1095
            elif precio <= 25000:
                return 2190
            elif precio <= 33000:
                return 2628
            else:
                return 0
        
        # Aplicar comisión condicional
        comision_adicional = precio_sin_comision.apply(calcular_comision_adicional)
        precio_estimado_venta = precio_sin_comision + comision_adicional
        
        df_display['Precio MercadoLibre (ARS)'] = precio_estimado_venta
        
        # Mejorar nombres de columnas para mayor claridad
        df_display.columns = ['Producto', 'Precio ARS', 'Cantidad', 'Precio USD', 'CBM Total', 'Precio MercadoLibre']
        
    except Exception as e:
        st.error(f"❌ Error al preparar la tabla de productos: {e}")
        st.info("💡 Verifica que los productos tengan todos los datos necesarios")
        st.stop()

    # Calcular altura dinámica basada en el número de productos
    # Altura base: 35px por fila + 60px para el header + 20px de padding
    num_productos = len(df_display)
    altura_dinamica = max(200, (num_productos * 35) + 80)  # Mínimo 200px, máximo según productos
    
    # Mostrar tabla mejorada con Streamlit nativo
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=altura_dinamica,  # Altura dinámica basada en el número de productos
        column_config={
            'Producto': st.column_config.TextColumn(
                '📦 Producto',
                width='small',
                help='Nombre del producto',
                max_chars=30  # Reducir caracteres para mejor visualización
            ),
            'Precio ARS': st.column_config.NumberColumn(
                '💵 ARS',
                format="$%.0f",
                help='Precio unitario final en pesos argentinos',
                width='small'
            ),
            'Cantidad': st.column_config.NumberColumn(
                '📊 Cantidad',
                format="%d",
                help='Cantidad total de unidades',
                width='small'
            ),
            'Precio USD': st.column_config.NumberColumn(
                '💰 USD',
                format="$%.0f",
                help='Precio unitario final en dólares',
                width='small'
            ),
            'CBM Total': st.column_config.NumberColumn(
                '📦 CBM Total',
                format="%.2f",
                help='Volumen total en metros cúbicos',
                width='small'
            ),
            'Precio MercadoLibre': st.column_config.NumberColumn(
                '🛒 Precio MercadoLibre',
                format="$%.0f",
                help='Precio de venta para MercadoLibre con 100% ganancia + 21% IVA + 15% comisión + comisión por rango',
                width='small'
            ),

        }
    )
    
    # KPIs de Impuestos y Derechos debajo de la tabla
    st.markdown("### 🏛️ Impuestos y Derechos")
    col_imp1, col_imp2, col_imp3, col_imp4 = st.columns(4)

    with col_imp1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">DDI Total</div>
            <div class="result-value">${total_ddi_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_imp2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Tasas Estadísticas</div>
            <div class="result-value">${total_tasas_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_imp3:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Antidumping</div>
            <div class="result-value">${total_antidumping_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_imp4:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Costo Base Total</div>
            <div class="result-value">${total_costo_base_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    # KPIs de Servicios y Gastos Fijos debajo de la tabla
    st.markdown("### 🛠️ Servicios y Gastos Fijos")
    col_serv1, col_serv2, col_serv3, col_serv4 = st.columns(4)
    
    with col_serv1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Agente</div>
            <div class="result-value">${total_agente_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_serv2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Despachante</div>
            <div class="result-value">${total_despachante_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_serv3:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Gastos Fijos</div>
            <div class="result-value">${gastos_fijos_total_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_serv4:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Costo Total Final</div>
            <div class="result-value">${total_costo_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)

    # --- KPIs DETALLADOS DE COSTOS ---
    st.markdown(
        """
<div class="section-header">
    <h2>Costos detallados</h2>
</div>
""",
        unsafe_allow_html=True
    )
    
    # KPIs de Costos Base
    st.markdown("### 🏷️ Costos Base")
    col_base1, col_base2, col_base3, col_base4 = st.columns(4)
    
    with col_base1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">FOB Total</div>
            <div class="result-value">${df_productos['FOB (USD)'].sum():,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_base2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Seguro</div>
            <div class="result-value">${total_seguro_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_base3:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Flete Total</div>
            <div class="result-value">${flete_total_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_base4:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">CIF Total</div>
            <div class="result-value">${df_productos['CIF (USD)'].sum():,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    

    
    # KPIs de Impuestos Adicionales
    st.markdown("### 💸 Impuestos Adicionales")
    st.markdown("")  # Espacio adicional
    col_imp_adic1, col_imp_adic2, col_imp_adic3, col_imp_adic4 = st.columns(4)
    
    with col_imp_adic1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">IVA Crédito Fiscal</div>
            <div class="result-value">${total_iva_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)

    with col_imp_adic2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">IVA Adicional</div>
            <div class="result-value">${total_iva_adic_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_imp_adic3:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Ganancias Anticipo</div>
            <div class="result-value">${total_ganancias_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_imp_adic4:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">IIBB Anticipo</div>
            <div class="result-value">${total_iibb_usd:,.0f}</div>
            <div class="result-label">USD</div>
        </div>
        """, unsafe_allow_html=True)
    

    
    # KPIs en Pesos Argentinos
    st.markdown("### 🇦🇷 Resumen en Pesos Argentinos")
    col_pesos1, col_pesos2, col_pesos3, col_pesos4 = st.columns(4)
    
    with col_pesos1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Costo Base</div>
            <div class="result-value">${total_costo_base_usd * precio_dolar:,.0f}</div>
            <div class="result-label">ARS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_pesos2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Impuestos Recuperables</div>
            <div class="result-value">${(total_iva_usd + total_iva_adic_usd + total_ganancias_usd + total_iibb_usd) * precio_dolar:,.0f}</div>
            <div class="result-label">ARS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_pesos3:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Gastos Fijos</div>
            <div class="result-value">${gastos_fijos_totales:,.0f}</div>
            <div class="result-label">ARS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_pesos4:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Costo Total Final</div>
            <div class="result-value">${total_costo_pesos:,.0f}</div>
            <div class="result-label">ARS</div>
        </div>
        """, unsafe_allow_html=True)
    


    # Expander para detalles completos editables
    with st.expander("🔍 Ver y Editar Análisis Detallado Completo", expanded=False):
        st.markdown("### 📋 Desglose Completo por Producto (Editable)")
        st.info("💡 **Puedes editar los datos directamente en la tabla. Los cambios se aplicarán automáticamente.**")
        
        # Crear tabla detallada con todas las columnas
        df_detailed = df_productos.copy()
        
        # Definir columnas editables (solo los datos de entrada, no los calculados)
        editable_columns = {
            'Nombre': st.column_config.TextColumn('Producto', width='medium'),
            'Cantidad Total': st.column_config.NumberColumn('Cantidad', format="%d", min_value=1),
            'CBM Total': st.column_config.NumberColumn('CBM (m³)', format="%.4f", min_value=0.0001),
            'Peso Total (kg)': st.column_config.NumberColumn('Peso (kg)', format="%.0f", min_value=0.1),
            'Precio FOB (USD)': st.column_config.NumberColumn('FOB USD', format="$%.2f", min_value=0.01),
            'DDI (%)': st.column_config.NumberColumn('DDI %', format="%.2f%%", min_value=0.0, max_value=100.0),
            'Antidumping (USD)': st.column_config.NumberColumn('Antidumping USD', format="$%.2f", min_value=0.0)
        }
        
        # Definir columnas de solo lectura (calculadas)
        readonly_columns = {
            'FOB (USD)': st.column_config.NumberColumn('FOB USD', format="$%.2f"),
            'Seguro (USD)': st.column_config.NumberColumn('Seguro USD', format="$%.2f"),
            'Flete por Producto (USD)': st.column_config.NumberColumn('Flete USD', format="$%.2f"),
            'CIF (USD)': st.column_config.NumberColumn('CIF USD', format="$%.2f"),
            'DDI (USD)': st.column_config.NumberColumn('DDI USD', format="$%.2f"),
            'Tasas (USD)': st.column_config.NumberColumn('Tasas USD', format="$%.2f"),
            'Costo Base (USD)': st.column_config.NumberColumn('Costo Base USD', format="$%.2f"),
            'IVA (USD)': st.column_config.NumberColumn('IVA USD', format="$%.2f"),
            'IVA Adicional (USD)': st.column_config.NumberColumn('IVA Adicional USD', format="$%.2f"),
            'Ganancias (USD)': st.column_config.NumberColumn('Ganancias USD', format="$%.2f"),
            'IIBB (USD)': st.column_config.NumberColumn('IIBB USD', format="$%.2f"),
            'Agente (USD)': st.column_config.NumberColumn('Agente USD', format="$%.2f"),
            'Despachante (USD)': st.column_config.NumberColumn('Despachante USD', format="$%.2f"),
            'Gastos Fijos por Producto (USD)': st.column_config.NumberColumn('Gastos Fijos USD', format="$%.2f"),
            'Verificación Gastos Fijos (%)': st.column_config.NumberColumn('Verif. Gastos Fijos %', format="%.2f%%"),
            'Costo sin Impuestos Recuperables (USD)': st.column_config.NumberColumn('Costo sin Recuperables USD', format="$%.2f"),
            'Costo con Impuestos Recuperables (USD)': st.column_config.NumberColumn('Costo con Recuperables USD', format="$%.2f"),
            'Costo Final por Producto (USD)': st.column_config.NumberColumn('Costo Final USD', format="$%.2f"),
            'Precio Unitario Final (USD)': st.column_config.NumberColumn('Precio Unitario USD', format="$%.2f"),
            'Precio Unitario Final (Pesos)': st.column_config.NumberColumn('Precio Unitario ARS', format="$%.2f"),
            'Comisión Adicional (ARS)': st.column_config.NumberColumn('Comisión Adicional ARS', format="$%.2f"),
            'Precio MercadoLibre (ARS)': st.column_config.NumberColumn('Precio MercadoLibre ARS', format="$%.2f"),
            'CBM por Producto': st.column_config.NumberColumn('CBM por Unidad', format="%.4f"),
            '% del CBM del Contenedor': st.column_config.NumberColumn('% CBM Contenedor', format="%.2f%%"),
            '% del CBM Utilizado': st.column_config.NumberColumn('% CBM Utilizado', format="%.2f%%"),
            'Verificación Flete (%)': st.column_config.NumberColumn('Verif. Flete %', format="%.2f%%"),
            '% del Peso': st.column_config.NumberColumn('% Peso', format="%.2f%%"),
            '% del Costo': st.column_config.NumberColumn('% Costo', format="%.2f%%")
        }
        
        # Combinar configuraciones
        column_config = {**editable_columns, **readonly_columns}
        
        # Mostrar tabla editable
        edited_df = st.data_editor(
            df_detailed,
            use_container_width=True,
            hide_index=True,
            height=400,
            column_config=column_config,
            num_rows="dynamic",
            key="detailed_editor"
        )
        
        # Detectar cambios y recalcular
        if not edited_df.equals(df_productos):
            st.success("🔄 **Cambios detectados. Recalculando...**")
            
            # Convertir el DataFrame editado de vuelta a la lista de productos
            productos_editados = edited_df.to_dict('records')
            
            # Actualizar session_state
            st.session_state['productos'] = productos_editados
            
            # Guardar en CSV
            try:
                df_editado_para_csv = pd.DataFrame(productos_editados)
                df_editado_para_csv.to_csv(PRODUCTOS_CSV, index=False)
                st.success("✅ **Datos guardados y recalculados automáticamente.**")
                
                # Rerun para actualizar todos los cálculos
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error al guardar los cambios: {e}")
        
        # Botones de acción
        st.markdown("### 🛠️ Acciones")
        col_actions1, col_actions2, col_actions3 = st.columns(3)
        
        with col_actions1:
            if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                try:
                    # Convertir el DataFrame editado a lista de productos
                    productos_editados = edited_df.to_dict('records')
                    
                    # Actualizar session_state
                    st.session_state['productos'] = productos_editados
                    
                    # Guardar en CSV
                    df_editado_para_csv = pd.DataFrame(productos_editados)
                    df_editado_para_csv.to_csv(PRODUCTOS_CSV, index=False)
                    
                    st.success("✅ **Cambios guardados exitosamente.**")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {e}")
        
        with col_actions2:
            # Selector de producto a eliminar
            if len(df_detailed) > 0:
                productos_para_eliminar = [f"{i+1}. {row['Nombre']}" for i, row in df_detailed.iterrows()]
                producto_a_eliminar = st.selectbox(
                    "🗑️ Seleccionar producto a eliminar:",
                    productos_para_eliminar,
                    key="eliminar_producto_selector"
                )
                
                if st.button("❌ Eliminar Producto Seleccionado", type="secondary", use_container_width=True):
                    try:
                        # Obtener el índice del producto seleccionado
                        indice_eliminar = productos_para_eliminar.index(producto_a_eliminar)
                        
                        # Eliminar el producto de la lista
                        productos_actuales = st.session_state['productos'].copy()
                        producto_eliminado = productos_actuales.pop(indice_eliminar)
                        
                        # Actualizar session_state
                        st.session_state['productos'] = productos_actuales
                        
                        # Guardar en CSV
                        df_actualizado = pd.DataFrame(productos_actuales)
                        df_actualizado.to_csv(PRODUCTOS_CSV, index=False)
                        
                        st.success(f"✅ **Producto eliminado:** {producto_eliminado['Nombre']}")
                        st.info("🔄 **Recalculando todos los valores...**")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al eliminar el producto: {e}")
            else:
                st.info("📦 No hay productos para eliminar")
        
        with col_actions3:
            if st.button("🔄 Recargar Datos", type="secondary", use_container_width=True):
                st.rerun()
        
        # Información adicional
        st.markdown("---")
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("**📊 Métricas Totales:**")
            st.write(f"• **Total de productos:** {len(df_productos)}")
            st.write(f"• **CBM total:** {total_cbm:.4f} m³")
            st.write(f"• **Peso total:** {total_peso:,.0f} kg")
            st.write(f"• **Costo total:** ${total_costo_usd:,.2f} USD")
        
        with col_info2:
            st.markdown("**💡 Información:**")
            st.write("• Los gastos fijos se distribuyen proporcionalmente por CBM")
            st.write("• El DDI se calcula sobre el valor CIF")
            st.write("• Los impuestos adicionales se calculan sobre el valor IVA")
            st.write("• El precio unitario incluye todos los costos")
    
    # Botón para limpiar toda la tabla
    st.markdown("---")
    col_clean1, col_clean2, col_clean3 = st.columns([1, 2, 1])
    
    with col_clean2:
        if st.button("🗑️ Limpiar Contenedor Completo", type="secondary", use_container_width=True, help="Elimina todos los productos del contenedor y limpia la base de datos"):
            try:
                # Limpiar session_state
                st.session_state['productos'] = []
                
                # Eliminar archivo CSV si existe
                if os.path.exists(PRODUCTOS_CSV):
                    os.remove(PRODUCTOS_CSV)
                
                # Mostrar mensaje de éxito
                st.success("✅ Contenedor limpiado completamente. Todos los productos han sido eliminados.")
                st.info("💡 El contenedor está ahora vacío. Puedes agregar nuevos productos desde el análisis individual.")
                
                # Rerun para actualizar la interfaz
                st.rerun()
    
            except Exception as e:
                st.error(f"❌ Error al limpiar el contenedor: {e}")
    
    st.markdown("---")
    
    # Exportar datos
    st.markdown(
        """
<div class="kpi-header">
    <h3>📤 Exportar Datos</h3>
    <p>Descarga los resultados del análisis en diferentes formatos</p>
</div>
""",
        unsafe_allow_html=True
    )
    
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        csv_completo = df_productos.to_csv(index=False)
        st.download_button(
            label="📄 Exportar tabla completa (CSV)",
            data=csv_completo,
            file_name=f"contenedor_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_exp2:
        resumen_ejecutivo = f"""
RESUMEN EJECUTIVO DEL CONTENEDOR
================================

Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Tipo de cambio: ${precio_dolar:,.2f}

RESUMEN GENERAL:
- Total de productos: {len(st.session_state['productos'])}
- CBM total: {total_cbm:.2f} m³
- Peso total: {total_peso:,.0f} kg
- Costo total final: ${total_costo_pesos:,.2f} pesos
- Contenedores necesarios: {contenedores_necesarios_total:.2f}

PRODUCTOS INCLUIDOS:
"""
        for i, prod in enumerate(st.session_state['productos'], 1):
            prod_data = df_productos[df_productos['Nombre'] == prod['Nombre']].iloc[0]
            resumen_ejecutivo += f"""
{i}. {prod['Nombre']}
   - Cantidad: {prod['Cantidad Total']:,} unidades
   - DDI: {prod_data['DDI (%)']:.1f}%
   - Precio unitario final: ${prod_data['Precio Unitario Final (USD)']:.2f} USD
   - CBM: {prod['CBM Total']:.4f} m³
   - Costo final: ${prod_data['Costo Final por Producto (USD)']:.2f} USD
"""
        st.download_button(
            label="📋 Exportar resumen ejecutivo",
            data=resumen_ejecutivo,
            file_name=f"resumen_contenedor_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
else:
    # Mensaje simple cuando no hay productos
    st.markdown("## 🚢 Contenedor Vacío")
    st.info("No hay productos en el contenedor.")
    st.info("💡 Ve al análisis individual para agregar productos.") 