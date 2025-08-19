import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import warnings
import io
import json
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Costos Individual",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
CONTAINER_40HQ_CBM = 70.0

# Inicializar session_state para persistir valores del sidebar
if 'precio_dolar' not in st.session_state:
    st.session_state.precio_dolar = 1000.0
if 'ddi_pct' not in st.session_state:
    st.session_state.ddi_pct = 18.0
if 'tasas_pct' not in st.session_state:
    st.session_state.tasas_pct = 3.0
if 'iva_pct' not in st.session_state:
    st.session_state.iva_pct = 21.0
if 'iva_adic_pct' not in st.session_state:
    st.session_state.iva_adic_pct = 20.0
if 'ganancias_pct' not in st.session_state:
    st.session_state.ganancias_pct = 6.0
if 'iibb_pct' not in st.session_state:
    st.session_state.iibb_pct = 2.0
if 'seguro_pct' not in st.session_state:
    st.session_state.seguro_pct = 0.5
if 'agente_pct' not in st.session_state:
    st.session_state.agente_pct = 4.0
if 'despachante_pct' not in st.session_state:
    st.session_state.despachante_pct = 1.0

# Inicializar lista de productos
if 'productos' not in st.session_state:
    st.session_state['productos'] = []

# Cargar productos desde CSV si existe (para mantener consistencia entre módulos)
if os.path.exists('productos_guardados.csv'):
    try:
        df_csv = pd.read_csv('productos_guardados.csv')
        if not df_csv.empty:
            st.session_state['productos'] = df_csv.to_dict('records')
    except Exception as e:
        # Si hay error al cargar, mantener la lista vacía
        st.session_state['productos'] = []

# CSS personalizado mejorado con colores de MercadoLibre
st.markdown("""
<style>
    /* Ocultar menú automático de páginas de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ocultar el menú de páginas en el sidebar */
    .css-1d391kg {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Importar fuentes de Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
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
    }
    
    /* Estilos globales */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Barra de navegación superior con estilo MercadoLibre */
    .navbar {
        background: linear-gradient(135deg, var(--ml-white) 0%, var(--ml-gray-very-light) 100%);
        padding: 1.5rem 2rem;
        margin: -1rem -2rem 2rem -2rem;
        border-bottom: 2px solid var(--ml-yellow);
        box-shadow: var(--shadow-lg);
        position: sticky;
        top: 0;
        z-index: 1000;
        backdrop-filter: blur(20px);
    }
    
    .navbar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .navbar-brand {
        font-size: 1.75rem;
        font-weight: 800;
        background: var(--background-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-decoration: none;
        letter-spacing: -0.025em;
    }
    
    .navbar-menu {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    
    .nav-item {
        position: relative;
    }
    
    .nav-link {
        background: linear-gradient(135deg, var(--ml-white) 0%, var(--ml-gray-very-light) 100%);
        color: var(--ml-gray-dark);
        padding: 0.875rem 1.75rem;
        text-decoration: none;
        border-radius: var(--border-radius);
        font-weight: 700;
        font-size: 0.875rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-md);
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        text-shadow: none;
        border: 2px solid var(--border-color);
        position: relative;
        overflow: hidden;
    }
    
    .nav-link::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .nav-link:hover::before {
        left: 100%;
    }
    
    .nav-link:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
        color: var(--ml-gray-dark);
        text-decoration: none;
        background: linear-gradient(135deg, var(--ml-gray-very-light) 0%, #E0E0E0 100%);
        border-color: var(--ml-yellow);
    }
    
    .nav-link.active {
        background: var(--background-gradient);
        box-shadow: var(--shadow-xl);
        color: var(--ml-gray-dark);
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 2px solid var(--ml-yellow-dark);
        font-weight: 800;
    }
    
    .nav-link.active:hover {
        background: linear-gradient(135deg, var(--ml-yellow-dark) 0%, var(--ml-yellow) 100%);
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
    }
    
    .main-header {
        font-size: 2.25rem;
        font-weight: 800;
        background: var(--background-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: -0.025em;
        line-height: 1.1;
        position: relative;
    }
    
    .subtitle {
        font-size: 1.125rem;
        color: var(--ml-gray-medium);
        text-align: center;
        margin-bottom: 3rem;
        line-height: 1.6;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Contenedores de sección con estilo MercadoLibre */
    .section-container {
        background: linear-gradient(135deg, var(--ml-white) 0%, var(--ml-gray-very-light) 100%);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        position: relative;
        overflow: hidden;
    }
    
    .section-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--background-gradient);
    }
    
    .section-container:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--ml-gray-dark);
        margin-bottom: 1.5rem;
        text-align: center;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: var(--background-gradient);
        border-radius: 2px;
    }
    
    /* Tarjetas de resultados con estilo MercadoLibre */
    .result-card {
        background: linear-gradient(135deg, var(--ml-white) 0%, var(--ml-gray-very-light) 100%);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
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
        height: 3px;
        background: var(--background-gradient);
    }
    
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--ml-yellow);
    }
    
    .result-label {
        font-size: 0.875rem;
        color: var(--ml-gray-medium);
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .result-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: var(--ml-gray-dark);
        margin-bottom: 0.25rem;
    }
    
    /* Información del contenedor con estilo MercadoLibre */
    .container-info {
        background: var(--background-gradient-blue);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--ml-blue-dark);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .container-info::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--ml-yellow);
    }
    
    .container-info:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .container-info h4 {
        color: var(--ml-white);
        font-size: 0.875rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Cajas de información con estilo MercadoLibre */
    .info-box {
        background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FB 100%);
        border: 2px solid var(--ml-blue);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }
    
    .info-box h3 {
        color: var(--ml-blue-dark);
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .info-box p {
        color: var(--ml-gray-dark);
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    
    /* Cajas de éxito con estilo MercadoLibre */
    .success-box {
        background: linear-gradient(135deg, #E8F5E8 0%, #D1E9D1 100%);
        border: 2px solid var(--ml-green);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }
    
    .success-box h3 {
        color: var(--ml-green);
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    /* Cajas de error con estilo MercadoLibre */
    .error-box {
        background: linear-gradient(135deg, #FDE8E8 0%, #FBD1D1 100%);
        border: 2px solid var(--ml-red);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }
    
    .error-box h3 {
        color: var(--ml-red);
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    /* Animaciones */
    .fade-in {
        animation: fadeIn 0.8s ease-in-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Estilos para botones con colores de MercadoLibre */
    .stButton > button {
        background: var(--background-gradient);
        color: var(--ml-gray-dark);
        border: 2px solid var(--ml-yellow-dark);
        border-radius: var(--border-radius);
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--ml-yellow-dark) 0%, var(--ml-yellow) 100%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* Sidebar con estilo MercadoLibre */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--ml-white) 0%, var(--ml-gray-very-light) 100%);
        border-right: 2px solid var(--ml-yellow);
    }
    
    /* Inputs con estilo MercadoLibre */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border: 2px solid var(--border-color);
        border-radius: var(--border-radius);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--ml-yellow);
        box-shadow: 0 0 0 3px rgba(255, 230, 0, 0.1);
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
    if st.button("📦 Contenedor", key="nav-container", use_container_width=True):
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

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 💱 Tipo de Cambio")
    
    # Obtener el valor actual del session_state
    precio_dolar_actual = st.session_state.get('precio_dolar', 1000.0)
    
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
    
    precio_dolar = st.number_input(
        "Precio del dólar (pesos)",
        min_value=0,
        value=int(precio_dolar_actual),
        step=1,
        key="precio_dolar_home",
        help="Ingresa el tipo de cambio actual USD/ARS"
    )
    
    # Actualizar session_state si cambió el valor
    if precio_dolar != precio_dolar_actual:
        st.session_state['precio_dolar'] = precio_dolar
        # Guardar en archivo de configuración
        config = {}
        try:
            if os.path.exists('container_config.json'):
                with open('container_config.json', 'r') as f:
                    config = json.load(f)
        except:
            config = {}
        
        config['precio_dolar'] = precio_dolar
        with open('container_config.json', 'w') as f:
            json.dump(config, f)
        
        st.success(f"✅ Tipo de cambio actualizado: ${precio_dolar:,.0f} pesos/USD")
    
    st.markdown("### 🎯 Configuración de Costos (No Recuperables)")
    ddi_pct = st.number_input(
        "Derechos de Importación (%)",
        min_value=0,
        value=int(st.session_state.ddi_pct),
        step=1,
        key="ddi_pct",
        help="Porcentaje de derechos de importación aplicable"
    )
    tasas_pct = st.number_input(
        "Tasas Estadísticas (%)",
        min_value=0,
        value=int(st.session_state.tasas_pct),
        step=1,
        key="tasas_pct",
        help="Porcentaje de tasas estadísticas"
    )
    seguro_pct = st.number_input(
        "Seguro (%)",
        min_value=0,
        value=int(st.session_state.seguro_pct),
        step=1,
        key="seguro_pct",
        help="Porcentaje de seguro sobre FOB"
    )
    agente_pct = st.number_input(
        "Agente (%)",
        min_value=0,
        value=int(st.session_state.agente_pct),
        step=1,
        key="agente_pct",
        help="Porcentaje de agente sobre FOB"
    )
    despachante_pct = st.number_input(
        "Despachante de Aduana (%)",
        min_value=0,
        value=int(st.session_state.despachante_pct),
        step=1,
        key="despachante_pct",
        help="Porcentaje de despachante sobre FOB"
    )
    
    st.markdown("### 📊 Impuestos Recuperables")
    st.markdown("*Solo informativos - no afectan el costo final*")
    
    iva_pct = st.number_input(
        "IVA (%)",
        min_value=0,
        value=int(st.session_state.iva_pct),
        step=1,
        key="iva_pct",
        help="IVA que se recupera al vender"
    )
    iva_adic_pct = st.number_input(
        "IVA Adicional (%)",
        min_value=0,
        value=int(st.session_state.iva_adic_pct),
        step=1,
        key="iva_adic_pct",
        help="IVA adicional"
    )
    ganancias_pct = st.number_input(
        "Ganancias (%)",
        min_value=0,
        value=int(st.session_state.ganancias_pct),
        step=1,
        key="ganancias_pct",
        help="Anticipo de ganancias"
    )
    iibb_pct = st.number_input(
        "IIBB (%)",
        min_value=0,
        value=int(st.session_state.iibb_pct),
        step=1,
        key="iibb_pct",
        help="Anticipo de IIBB"
    )
    


# --- Uploader de archivo para carga masiva de productos ---
st.markdown("""
<div style="width: 100%; background: linear-gradient(135deg, #FFE600 0%, #FFF533 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <div style="color: #333333; font-size: 1.1rem; font-weight: 700; text-align: center;">📥 Carga Masiva de Productos desde Archivo de Proveedor</div>
</div>
""", unsafe_allow_html=True)



# Configuración de carga masiva
with st.expander("⚙️ Configuración de Carga Masiva", expanded=False):
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        st.session_state.overwrite_existing = st.checkbox(
            "🔄 Sobrescribir productos existentes",
            value=False,
            help="Si está marcado, reemplazará todos los productos existentes. Si no, agregará a la lista actual."
        )
        st.session_state.skip_duplicates = st.checkbox(
            "⏭️ Saltar productos duplicados",
            value=True,
            help="Si está marcado, no agregará productos con nombres que ya existen."
        )
    with col_config2:
        st.session_state.validate_data = st.checkbox(
            "✅ Validar datos antes de cargar",
            value=True,
            help="Realizar validaciones de datos antes de procesar la carga."
        )
        st.session_state.auto_calculate = st.checkbox(
            "🧮 Calcular automáticamente",
            value=True,
            help="Calcular automáticamente CBM, peso y otros valores derivados."
        )

col_up1, col_up2 = st.columns([2,1])
with col_up1:
    archivo = st.file_uploader(
        "Selecciona un archivo Excel (.xlsx, .xls) o CSV con los productos a cargar",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=False
    )
with col_up2:
    # Crear y descargar ejemplos dinámicamente
    st.markdown("**📥 Descargar Ejemplos:**")
    
    # Ejemplo 1: Formato Estándar
    ejemplo_estandar = pd.DataFrame({
        'Nombre': ['Vaso Mug 12oz', 'Tumbler 30oz', 'Taza Cerámica', 'Botella Térmica'],
        'SKU': ['VM12-001', 'TB30-002', 'TC08-003', 'BT20-004'],
        'Cantidad por Carton': [100, 50, 200, 80],
        'Precio En USD': [0.85, 2.50, 0.45, 3.20],
        'CBM': [0.0346, 0.0520, 0.0280, 0.0450],
        'GW': [12.5, 18.2, 8.8, 15.6]
    })
    
    # Crear archivo Excel temporal
    temp_file_estandar = "temp_ejemplo_estandar.xlsx"
    with pd.ExcelWriter(temp_file_estandar, engine='openpyxl') as writer:
        ejemplo_estandar.to_excel(writer, sheet_name='Productos', index=False)
    
    with open(temp_file_estandar, 'rb') as f:
        excel_data_estandar = f.read()
    
    st.download_button(
        label="📊 Formato Estándar",
        data=excel_data_estandar,
        file_name="ejemplo_formato_estandar.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    # Limpiar archivo temporal
    if os.path.exists(temp_file_estandar):
        os.remove(temp_file_estandar)
    
    # Ejemplo 2: Formato Original
    ejemplo_original = pd.DataFrame({
        'Nombre': ['Vaso Mug 12oz', 'Tumbler 30oz', 'Taza Cerámica'],
        'SKU': ['VM12-001', 'TB30-002', 'TC08-003'],
        'Precio FOB (USD)': [0.85, 2.50, 0.45],
        'Cantidad Total': [1000, 500, 2000],
        'Piezas por Caja': [100, 50, 200],
        'Peso por Caja (kg)': [12.5, 18.2, 8.8],
        'Largo (cm)': [40, 35, 25],
        'Ancho (cm)': [30, 25, 20],
        'Alto (cm)': [25, 30, 15],
        'DDI (%)': [18.0, 25.0, 15.0]
    })
    
    # Crear archivo Excel temporal
    temp_file_original = "temp_ejemplo_original.xlsx"
    with pd.ExcelWriter(temp_file_original, engine='openpyxl') as writer:
        ejemplo_original.to_excel(writer, sheet_name='Productos', index=False)
    
    with open(temp_file_original, 'rb') as f:
        excel_data_original = f.read()
    
    st.download_button(
        label="📋 Formato Original",
        data=excel_data_original,
        file_name="ejemplo_formato_original.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    # Limpiar archivo temporal
    if os.path.exists(temp_file_original):
        os.remove(temp_file_original)

if archivo is not None:
    try:
        # Leer el archivo una sola vez
        if archivo.name.endswith('.csv'):
            df_upload = pd.read_csv(archivo)
        else:
            df_upload = pd.read_excel(archivo)
        
        # Guardar el DataFrame original para el procesamiento posterior
        df_original = df_upload.copy()
        
        # Intentar detectar el formato del archivo
        try:
            from procesador_formato_original import procesar_dataframe_formato_original
            from procesador_especifico_chino import procesar_dataframe_proveedor_chino
            
            # Primero intentar procesar como archivo de proveedor chino
            productos_procesados = procesar_dataframe_proveedor_chino(df_upload)
            
            if productos_procesados:
                st.success(f"✅ Archivo procesado como archivo de proveedor chino")
                st.info(f"📦 Se detectaron {len(productos_procesados)} productos")
                
                # Convertir a DataFrame para mostrar preview
                df_preview = pd.DataFrame(productos_procesados)
                
                # Mostrar preview
                with st.expander("👁️ Preview de Datos Procesados", expanded=True):
                    st.dataframe(df_preview.head(10), use_container_width=True)
                    if len(df_preview) > 10:
                        st.info(f"Mostrando 10 de {len(df_preview)} productos")
                
                # Guardar los productos procesados para usar en el botón
                st.session_state['productos_procesados'] = productos_procesados
                st.session_state['formato_detectado'] = 'chino'
                
                # Continuar con el procesamiento normal
            else:
                # Verificar si es formato original
                productos_procesados = procesar_dataframe_formato_original(df_upload)
                
                if productos_procesados:
                    st.success(f"✅ Archivo procesado como formato original de costos")
                    st.info(f"📦 Se detectaron {len(productos_procesados)} productos")
                    
                    # Convertir a DataFrame para mostrar preview
                    df_preview = pd.DataFrame(productos_procesados)
                    
                    # Mostrar preview
                    with st.expander("👁️ Preview de Datos Procesados", expanded=True):
                        st.dataframe(df_preview.head(10), use_container_width=True)
                        if len(df_preview) > 10:
                            st.info(f"Mostrando 10 de {len(df_preview)} productos")
                    
                    # Guardar los productos procesados para usar en el botón
                    st.session_state['productos_procesados'] = productos_procesados
                    st.session_state['formato_detectado'] = 'original'
                    
                    # Continuar con el procesamiento normal
                else:
                    # Verificar si es formato estándar
                    columnas_requeridas = [
                        'Nombre', 'Cantidad por Carton', 'Precio En USD', 'CBM', 'GW'
                    ]
                    
                    if all(col in df_upload.columns for col in columnas_requeridas):
                        st.success(f"✅ Archivo procesado como formato estándar")
                        st.info(f"📦 Se detectaron {len(df_upload)} filas")
                        
                        # Mostrar preview
                        with st.expander("👁️ Preview de Datos Procesados", expanded=True):
                            st.dataframe(df_upload.head(10), use_container_width=True)
                            if len(df_upload) > 10:
                                st.info(f"Mostrando 10 de {len(df_upload)} productos")
                        
                        # Guardar el DataFrame para usar en el botón
                        st.session_state['productos_procesados'] = None
                        st.session_state['formato_detectado'] = 'estandar'
                        
                        # Continuar con el procesamiento normal
                    else:
                        st.error(f"❌ Formato de archivo no reconocido")
                        st.error(f"Columnas encontradas: {', '.join(df_upload.columns)}")
                        st.error("El archivo debe tener uno de los siguientes formatos:")
                        st.error("• Formato chino: Archivos de proveedores con texto en chino")
                        st.error("• Formato original: Nombre, SKU, Precio FOB (USD), Cantidad Total, Piezas por Caja, Peso por Caja (kg), Largo (cm), Ancho (cm), Alto (cm), DDI (%)")
                        st.error("• Formato estándar: Nombre, Cantidad por Carton, Precio En USD, CBM, GW")
                        st.stop()
        except Exception as e:
            # Manejar cualquier error
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
            st.info("📋 Intentando procesar como archivo estándar...")
            
            # Columnas requeridas (formato simplificado para proveedores)
            columnas_requeridas = [
                'Nombre', 'Cantidad por Carton', 'Precio En USD', 'CBM', 'GW'
            ]
            
            # Columnas opcionales
            columnas_opcionales = ['SKU', 'Precio RMB']
            
            if not all(col in df_upload.columns for col in columnas_requeridas):
                st.error(f"El archivo debe contener las siguientes columnas: {', '.join(columnas_requeridas)}")
                st.error(f"Columnas encontradas: {', '.join(df_upload.columns)}")
                st.stop()
        except ImportError:
            # Si no están disponibles los procesadores, usar método estándar
            st.info("📋 Procesando como archivo estándar...")
            
            if archivo.name.endswith('.csv'):
                df_upload = pd.read_csv(archivo)
            else:
                df_upload = pd.read_excel(archivo)
            
            # Columnas requeridas (formato simplificado para proveedores)
            columnas_requeridas = [
                'Nombre', 'Cantidad por Carton', 'Precio En USD', 'CBM', 'GW'
            ]
            
            # Columnas opcionales
            columnas_opcionales = ['SKU', 'Precio RMB']
            
            if not all(col in df_upload.columns for col in columnas_requeridas):
                st.error(f"El archivo debe contener las siguientes columnas: {', '.join(columnas_requeridas)}")
                st.error(f"Columnas encontradas: {', '.join(df_upload.columns)}")
                st.stop()
        except Exception as e:
            # Manejar cualquier otro error
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
            st.info("📋 Intentando procesar como archivo estándar...")
            
            try:
                if archivo.name.endswith('.csv'):
                    df_upload = pd.read_csv(archivo)
                else:
                    df_upload = pd.read_excel(archivo)
                
                # Columnas requeridas (formato simplificado para proveedores)
                columnas_requeridas = [
                    'Nombre', 'Cantidad por Carton', 'Precio En USD', 'CBM', 'GW'
                ]
                
                # Columnas opcionales
                columnas_opcionales = ['SKU', 'Precio RMB']
                
                if not all(col in df_upload.columns for col in columnas_requeridas):
                    st.error(f"El archivo debe contener las siguientes columnas: {', '.join(columnas_requeridas)}")
                    st.error(f"Columnas encontradas: {', '.join(df_upload.columns)}")
                    st.stop()
            except Exception as e2:
                st.error(f"❌ Error al leer el archivo: {str(e2)}")
                st.error("Asegúrate de que el archivo tenga el formato correcto y las columnas requeridas.")
                st.stop()
        
        # Validaciones de datos si está habilitado (para ambos formatos)
        if st.session_state.get('validate_data', True):
            errores_validacion = []
            
            # Solo validar si no es formato chino (ya que los productos chinos ya están procesados)
            if st.session_state.get('formato_detectado') != 'chino':
                # Determinar qué DataFrame usar para validaciones
                df_para_validar = df_upload
                if st.session_state.get('formato_detectado') == 'original' and st.session_state.get('productos_procesados'):
                    # Para formato original, validar los datos originales
                    df_para_validar = df_original
                
                # Validar que no haya valores negativos o cero en campos críticos
                for idx, row in df_para_validar.iterrows():
                    # Validar precio (USD o RMB)
                    precio_usd = row.get('Precio FOB (USD)', 0)  # Formato original usa 'Precio FOB (USD)'
                    precio_rmb = row.get('Precio RMB', 0)
                    
                    if precio_usd <= 0 and precio_rmb <= 0:
                        errores_validacion.append(f"Fila {idx+1}: Debe tener Precio FOB (USD) o Precio RMB mayor a 0")
                    elif precio_rmb > 0 and precio_usd <= 0:
                        # Convertir RMB a USD
                        precio_usd = precio_rmb / 7.10
                        df_para_validar.loc[idx, 'Precio FOB (USD)'] = precio_usd
                    
                    # Validar cantidad según el formato
                    if st.session_state.get('formato_detectado') == 'original':
                        # Formato original
                        if row['Cantidad Total'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: Cantidad Total debe ser mayor a 0")
                        if row['Piezas por Caja'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: Piezas por Caja debe ser mayor a 0")
                        if row['Peso por Caja (kg)'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: Peso por Caja (kg) debe ser mayor a 0")
                        if row['Largo (cm)'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: Largo (cm) debe ser mayor a 0")
                        if row['Ancho (cm)'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: Ancho (cm) debe ser mayor a 0")
                        if row['Alto (cm)'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: Alto (cm) debe ser mayor a 0")
                    else:
                        # Formato estándar
                        if row['Cantidad por Carton'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: Cantidad por Carton debe ser mayor a 0")
                        if row['CBM'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: CBM debe ser mayor a 0")
                        if row['GW'] <= 0:
                            errores_validacion.append(f"Fila {idx+1}: GW debe ser mayor a 0")
                
                if errores_validacion:
                    st.error("❌ Errores de validación encontrados:")
                    for error in errores_validacion:
                        st.error(f"• {error}")
                    st.stop()
        
        # Verificar duplicados en el archivo
        if st.session_state.get('formato_detectado') in ['original', 'chino'] and st.session_state.get('productos_procesados'):
            # Para formato original o chino, verificar duplicados en los productos procesados
            nombres_archivo = [prod['Nombre'] for prod in st.session_state['productos_procesados']]
        else:
            # Para formato estándar, verificar duplicados en el DataFrame
            nombres_archivo = df_upload['Nombre'].tolist()
        
        duplicados_archivo = [nombre for nombre in nombres_archivo if nombres_archivo.count(nombre) > 1]
        
        # Mostrar información sobre duplicados en el archivo
        if duplicados_archivo:
            st.warning(f"⚠️ El archivo contiene {len(set(duplicados_archivo))} productos duplicados: {', '.join(set(duplicados_archivo))}")
        
        # Verificar productos existentes
        productos_existentes = []
        if 'productos' in st.session_state and st.session_state['productos']:
            productos_existentes = [prod['Nombre'] for prod in st.session_state['productos']]
        
        # Mostrar información resumida
        if st.session_state.get('formato_detectado') == 'original':
            st.success(f"✅ Archivo '{archivo.name}' procesado como formato original ({len(st.session_state.get('productos_procesados', []))} productos)")
        else:
            st.success(f"✅ Archivo '{archivo.name}' cargado correctamente ({len(df_upload)} productos)")
        
        if productos_existentes and not st.session_state.get('overwrite_existing', False):
            st.info(f"ℹ️ Se agregarán a los {len(productos_existentes)} productos existentes en la lista.")
        elif st.session_state.get('overwrite_existing', False):
            st.warning("⚠️ Se sobrescribirán todos los productos existentes.")
        
        # Botón para procesar la carga
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🚀 Cargar Productos al Contenedor", type="primary", use_container_width=True):
                    # Guardar información para mostrar después del rerun
                    st.session_state['carga_masiva_info'] = {
                        'archivo_nombre': archivo.name,
                        'productos_archivo': len(df_upload),
                        'productos_existentes': len(productos_existentes),
                        'overwrite': st.session_state.get('overwrite_existing', False)
                    }
                    
                    # Limpiar productos existentes si se va a sobrescribir
                    if st.session_state.get('overwrite_existing', False):
                        st.session_state['productos'] = []
                    
                    productos_agregados = 0
                    productos_duplicados = 0
                    productos_omitidos = 0
                    
                    # Determinar qué datos procesar
                    if st.session_state.get('formato_detectado') in ['original', 'chino'] and st.session_state.get('productos_procesados'):
                        # Usar productos ya procesados del formato original o chino
                        datos_a_procesar = st.session_state['productos_procesados']
                        procesando_formato_original = True
                    else:
                        # Usar DataFrame normal
                        datos_a_procesar = df_upload.to_dict('records')
                        procesando_formato_original = False
                    
                    # Procesar cada fila del archivo
                    for idx, row_data in enumerate(datos_a_procesar):
                        if procesando_formato_original:
                            # Formato original ya procesado
                            nombre_producto = row_data['Nombre']
                            precio_usd = row_data['Precio En USD']
                            cantidad_por_carton = row_data['Cantidad por Carton']
                            cbm_por_carton = row_data['CBM']
                            peso_por_carton = row_data['GW']
                        else:
                            # Formato estándar
                            nombre_producto = row_data['Nombre']
                            
                            # Verificar si el producto ya existe
                            if st.session_state.get('skip_duplicates', True) and nombre_producto in productos_existentes:
                                productos_omitidos += 1
                                continue
                            
                            # Obtener precio en USD (convertir RMB si es necesario)
                            precio_usd = row_data.get('Precio En USD', 0)
                            precio_rmb = row_data.get('Precio RMB', 0)
                            
                            if precio_rmb > 0 and precio_usd <= 0:
                                precio_usd = precio_rmb / 7.10  # Conversión RMB a USD
                            
                            # Valores predeterminados para campos no proporcionados
                            cantidad_por_carton = row_data['Cantidad por Carton']
                            cbm_por_carton = row_data['CBM']
                            peso_por_carton = row_data['GW']
                        
                        # Verificar si el producto ya existe (para formato original)
                        if st.session_state.get('skip_duplicates', True) and nombre_producto in productos_existentes:
                            productos_omitidos += 1
                            continue
                        
                        # Valores predeterminados
                        piezas_por_caja = 1  # Predeterminado: 1 pieza por caja
                        
                        # Usar DDI específico del producto si está disponible, sino usar el global
                        if procesando_formato_original and 'DDI (%)' in row_data:
                            ddi_producto_pct = row_data['DDI (%)']
                        else:
                            ddi_producto_pct = st.session_state.ddi_pct  # Usar DDI global
                        
                        # Cálculos derivados
                        cbm_caja = cbm_por_carton / cantidad_por_carton if cantidad_por_carton > 0 else 0
                        peso_por_caja = peso_por_carton / cantidad_por_carton if cantidad_por_carton > 0 else 0
                        
                        # Calcular dimensiones aproximadas (asumiendo caja cúbica)
                        dimension_aproximada = (cbm_caja * 1000000) ** (1/3)  # Convertir a cm
                        largo = ancho = alto = dimension_aproximada
                        
                        # Cálculos de contenedor
                        cajas_necesarias = cantidad_por_carton / piezas_por_caja  # Total de cajas necesarias para la cantidad
                        cajas_por_contenedor = int(CONTAINER_40HQ_CBM / cbm_caja)  # Cuántas cajas caben en un contenedor
                        piezas_por_contenedor = cajas_por_contenedor * piezas_por_caja  # Cuántas piezas caben en un contenedor
                        cbm_total = cbm_por_carton
                        peso_total = peso_por_carton
                        
                        # Cálculos de costos básicos
                        fob_usd = precio_usd * cantidad_por_carton
                        seguro = fob_usd * (st.session_state.seguro_pct / 100)
                        
                        # CIF = FOB + Seguro (el flete se calcula después en el contenedor)
                        cif = fob_usd + seguro
                        
                        # DDI y Tasas sobre CIF
                        ddi = cif * (ddi_producto_pct / 100)
                        tasas = cif * (st.session_state.tasas_pct / 100)
                        
                        # VALOR IVA = CIF + DDI + Tasas
                        valor_iva = cif + ddi + tasas
                        
                        # Impuestos sobre VALOR IVA
                        iva = valor_iva * (st.session_state.iva_pct / 100)
                        iva_adicional = valor_iva * (st.session_state.iva_adic_pct / 100)
                        ganancias = valor_iva * (st.session_state.ganancias_pct / 100)
                        iibb = valor_iva * (st.session_state.iibb_pct / 100)
                        
                        # Otros gastos sobre FOB
                        agente = fob_usd * (st.session_state.agente_pct / 100)
                        despachante = fob_usd * (st.session_state.despachante_pct / 100)
                        
                        # Costo total con impuestos (sin IVAs)
                        costo_total_usd = cif + ddi + tasas + agente + despachante  # Solo costos no recuperables (carga masiva sin gastos fijos)
                        precio_unitario_usd = costo_total_usd / cantidad_por_carton if cantidad_por_carton > 0 else 0
                        precio_unitario_pesos = precio_unitario_usd * st.session_state.precio_dolar
                        costo_total_pesos = costo_total_usd * st.session_state.precio_dolar
                        
                        # Agregar producto
                        st.session_state['productos'].append({
                            'Nombre': nombre_producto,
                            'SKU': row_data.get('SKU', f'SKU{idx+1:03d}'),  # Usar SKU del archivo o generar uno automático
                            'Precio FOB (USD)': precio_usd,
                            'Precio Final (USD)': precio_unitario_usd,
                            'Precio Final (Pesos)': precio_unitario_pesos,
                            'CBM por Caja': cbm_caja,
                            'Piezas por Caja': piezas_por_caja,
                            'Cajas por Contenedor': cajas_por_contenedor,
                            'Piezas por Contenedor': piezas_por_contenedor,
                            'Contenedores Necesarios': cbm_total / CONTAINER_40HQ_CBM,
                            'CBM Total': cbm_total,
                            'Peso por Caja (kg)': peso_por_caja,
                            'Peso Total (kg)': peso_total,
                            'Cantidad Total': cantidad_por_carton,
                            'Costo Total (USD)': costo_total_usd,
                            'Costo Total (Pesos)': costo_total_pesos,
                            'Flete por Producto (USD)': 0,
                            'Gastos Fijos por Producto (USD)': 0,
                            'Largo (cm)': largo,
                            'Ancho (cm)': ancho,
                            'Alto (cm)': alto,
                            'DDI (%)': ddi_producto_pct,
                        })
                        productos_agregados += 1
                    
                    # Guardar en CSV
                    if st.session_state['productos']:
                        df = pd.DataFrame(st.session_state['productos'])
                        df.to_csv('productos_guardados.csv', index=False)
                    
                    # Guardar resultado en session_state para mostrar después del rerun
                    st.session_state['carga_masiva_resultado'] = {
                        'productos_agregados': productos_agregados,
                        'productos_omitidos': productos_omitidos,
                        'productos_duplicados': productos_duplicados
                    }
                    
                    st.rerun()
            
            with col_btn2:
                if st.button("🗑️ Limpiar Datos", type="secondary", use_container_width=True):
                    st.session_state['productos'] = []
                    if os.path.exists('productos_guardados.csv'):
                        os.remove('productos_guardados.csv')
                    st.success("✅ Todos los productos han sido eliminados.")
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.error("Asegúrate de que el archivo tenga el formato correcto y las columnas requeridas.")

# Mostrar resultado de carga masiva si existe
if 'carga_masiva_resultado' in st.session_state:
    resultado = st.session_state['carga_masiva_resultado']
    info = st.session_state.get('carga_masiva_info', {})
    
    # Crear tarjetas de resumen
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    
    with col_res1:
        st.metric(
            label="📦 Productos Agregados",
            value=resultado['productos_agregados'],
            delta=f"desde {info.get('archivo_nombre', 'archivo')}"
        )
    
    with col_res2:
        st.metric(
            label="⏭️ Productos Omitidos",
            value=resultado['productos_omitidos'],
            delta="duplicados" if resultado['productos_omitidos'] > 0 else None
        )
    
    with col_res3:
        st.metric(
            label="⚠️ Duplicados en Archivo",
            value=resultado['productos_duplicados'],
            delta="encontrados" if resultado['productos_duplicados'] > 0 else None
        )
    
    with col_res4:
        total_productos = len(st.session_state.get('productos', []))
        st.metric(
            label="📊 Total Productos",
            value=total_productos,
            delta="en contenedor"
        )
    
    # Mostrar información adicional
    if info.get('overwrite', False):
        st.info("ℹ️ Se sobrescribieron todos los productos existentes.")
    elif info.get('productos_existentes', 0) > 0:
        st.info(f"ℹ️ Se agregaron a los {info['productos_existentes']} productos existentes.")
    
        # Limpiar los resultados para que no se muestren en la próxima carga
    del st.session_state['carga_masiva_resultado']
    if 'carga_masiva_info' in st.session_state:
        del st.session_state['carga_masiva_info']
    
    # Limpiar variables de formato detectado
    if 'productos_procesados' in st.session_state:
        del st.session_state['productos_procesados']
    if 'formato_detectado' in st.session_state:
        del st.session_state['formato_detectado']

# Sección 1: Información del Producto
st.markdown("""
<div style="width: 100%; background: linear-gradient(135deg, #FFE600 0%, #FFF533 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <div style="color: #333333; font-size: 1.3rem; font-weight: 700; text-align: center;">Agregar producto individualmente</div>
</div>
""", unsafe_allow_html=True)

# Fila 1: Nombre (100% ancho)
nombre = st.text_input(
    "Nombre del Producto",
    placeholder="Ej: Producto XYZ",
    help="Ingresa el nombre o descripción del producto"
)

# Fila 2: Precio y Cantidad (50% y 50%)
col_precio, col_cant = st.columns(2)
with col_precio:
    precio_u = st.number_input(
        "Precio Unitario FOB (USD)",
        min_value=0.0,
        value=10.0,
        step=0.001,
        format="%.3f",
        help="Precio por unidad en dólares (FOB)"
    )
with col_cant:
    cantidad = st.number_input(
        "Cantidad Total",
        min_value=1,
        value=1000,
        step=1,
        help="Cantidad total de unidades a importar"
    )

# Espaciado entre secciones
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Sección 2: Dimensiones del Producto
st.markdown("""
<div style="width: 100%; background: linear-gradient(135deg, #FFE600 0%, #FFF533 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <div style="color: #333333; font-size: 1.3rem; font-weight: 700; text-align: center;">📏 Dimensiones del Producto</div>
</div>
""", unsafe_allow_html=True)

# Opción para elegir método de entrada de CBM
metodo_cbm = st.radio(
    "¿Cómo quieres ingresar el CBM?",
    options=["📏 Dimensiones de la caja (Largo x Ancho x Alto)", "📦 CBM directo"],
    horizontal=True,
    help="Elige si quieres calcular el CBM desde las dimensiones o ingresarlo directamente"
)

if metodo_cbm == "📏 Dimensiones de la caja (Largo x Ancho x Alto)":
    # Mostrar campos de dimensiones
    col_dim1, col_dim2, col_dim3, col_dim4, col_dim5 = st.columns(5)
    
    with col_dim1:
        largo = st.number_input(
            "Largo (cm)",
            min_value=0.0,
            value=30.0,
            step=0.1,
            help="Largo de la caja en centímetros"
        )
    with col_dim2:
        ancho = st.number_input(
            "Ancho (cm)",
            min_value=0.0,
            value=20.0,
            step=0.1,
            help="Ancho de la caja en centímetros"
        )
    with col_dim3:
        alto = st.number_input(
            "Alto (cm)",
            min_value=0.0,
            value=15.0,
            step=0.1,
            help="Alto de la caja en centímetros"
        )
    with col_dim4:
        peso = st.number_input(
            "Peso por Caja (kg)",
            min_value=0.0,
            value=5.0,
            step=0.1,
            help="Peso de cada caja en kilogramos"
        )
    with col_dim5:
        pcs_ctn = st.number_input(
            "Piezas por Caja",
            min_value=1,
            value=10,
            step=1,
            help="Cantidad de piezas por caja/embalaje"
        )
    
    # Calcular CBM automáticamente
    cbm = (largo * ancho * alto) / 1_000_000  # Convertir cm³ a m³
    
    # Mostrar CBM calculado
    st.info(f"📊 **CBM calculado automáticamente:** {cbm:.6f} m³ (Largo: {largo}cm × Ancho: {ancho}cm × Alto: {alto}cm)")

else:
    # Mostrar campo de CBM directo
    col_cbm1, col_cbm2, col_cbm3 = st.columns(3)
    
    with col_cbm1:
        cbm = st.number_input(
            "CBM por Caja (m³)",
            min_value=0.0,
            value=0.009,
            step=0.001,
            format="%.6f",
            help="Volumen de cada caja en metros cúbicos"
        )
    with col_cbm2:
        peso = st.number_input(
            "Peso por Caja (kg)",
            min_value=0.0,
            value=5.0,
            step=0.1,
            help="Peso de cada caja en kilogramos"
        )
    with col_cbm3:
        pcs_ctn = st.number_input(
            "Piezas por Caja",
            min_value=1,
            value=10,
            step=1,
            help="Cantidad de piezas por caja/embalaje"
        )
    
    # Inicializar dimensiones en 0 para mantener compatibilidad
    largo = 0.0
    ancho = 0.0
    alto = 0.0

# Espaciado entre secciones
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Botón de cálculo
col_calc1, col_calc2, col_calc3 = st.columns([1, 2, 1])
with col_calc2:
    calcular = st.button("🚀 Calcular Costos Completos", use_container_width=True, type="primary")
    if calcular:
        st.session_state['calcular'] = True

# Espaciado después del botón
st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# Sección 3: Resultados
if calcular or ('calcular' in st.session_state and st.session_state['calcular']):
    # Validar que el CBM sea mayor que 0
    if cbm <= 0:
        st.error("❌ **Error:** El CBM debe ser mayor que 0. Por favor, ingresa un valor válido.")
        st.stop()
    
    # Validar que la cantidad sea mayor que 0
    if cantidad <= 0:
        st.error("❌ **Error:** La cantidad debe ser mayor que 0. Por favor, ingresa un valor válido.")
        st.stop()
    
    # Validar que las piezas por caja sea mayor que 0
    if pcs_ctn <= 0:
        st.error("❌ **Error:** Las piezas por caja debe ser mayor que 0. Por favor, ingresa un valor válido.")
        st.stop()
    
    # Cálculos básicos
    cajas_necesarias = cantidad / pcs_ctn  # Total de cajas necesarias para la cantidad
    cbm_total = cajas_necesarias * cbm  # CBM total basado en las cajas necesarias
    peso_total = cajas_necesarias * peso  # Peso total basado en las cajas necesarias
    
    # Verificar si excede el límite del contenedor
    if cbm_total > CONTAINER_40HQ_CBM:
        st.markdown(f"""
        <div class="error-box">
            <h3>⚠️ ¡Atención! Exceso de CBM</h3>
            <p><strong>CBM Total:</strong> {cbm_total:.4f} m³</p>
            <p><strong>Límite Contenedor 40HQ:</strong> {CONTAINER_40HQ_CBM} m³</p>
            <p><strong>Exceso:</strong> {cbm_total - CONTAINER_40HQ_CBM:.4f} m³</p>
            <p>Considera reducir la cantidad o usar múltiples contenedores.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Cálculos de contenedor
    cajas_por_contenedor = int(CONTAINER_40HQ_CBM / cbm)  # Cuántas cajas caben en un contenedor
    piezas_por_contenedor = cajas_por_contenedor * pcs_ctn  # Cuántas piezas caben en un contenedor
    contenedores_necesarios = cbm_total / CONTAINER_40HQ_CBM  # Cuántos contenedores necesitas basado en CBM
    
    # Cálculos de costos
    fob_por_pieza = precio_u  # Precio FOB por pieza individual
    
    seguro_por_pieza = fob_por_pieza * (seguro_pct / 100)
    cif_por_pieza = fob_por_pieza + seguro_por_pieza
    ddi_por_pieza = cif_por_pieza * (ddi_pct / 100)
    tasas_por_pieza = cif_por_pieza * (tasas_pct / 100)
    agente_por_pieza = fob_por_pieza * (agente_pct / 100)
    despachante_por_pieza = fob_por_pieza * (despachante_pct / 100)
    
    # Costo total por pieza (solo costos no recuperables)
    costo_unitario_usd = cif_por_pieza + ddi_por_pieza + tasas_por_pieza + agente_por_pieza + despachante_por_pieza
    
    # Costos totales para toda la cantidad
    fob = fob_por_pieza * cantidad
    seguro = seguro_por_pieza * cantidad
    cif = cif_por_pieza * cantidad
    ddi = ddi_por_pieza * cantidad
    tasas = tasas_por_pieza * cantidad
    agente = agente_por_pieza * cantidad
    despachante = despachante_por_pieza * cantidad
    
    # Impuestos recuperables (solo para información)
    iva = cif * (iva_pct / 100)
    iva_adic = cif * (iva_adic_pct / 100)
    ganancias = cif * (ganancias_pct / 100)
    iibb = cif * (iibb_pct / 100)
    
    costo_total_usd = cif + ddi + tasas + agente + despachante  # Solo costos no recuperables
    precio_unitario_usd = costo_unitario_usd  # Ya es por pieza individual

    # Conversiones a pesos
    fob_pesos = fob * precio_dolar
    seguro_pesos = seguro * precio_dolar
    cif_pesos = cif * precio_dolar
    ddi_pesos = ddi * precio_dolar
    tasas_pesos = tasas * precio_dolar
    iva_pesos = iva * precio_dolar
    iva_adic_pesos = iva_adic * precio_dolar
    ganancias_pesos = ganancias * precio_dolar
    iibb_pesos = iibb * precio_dolar
    agente_pesos = agente * precio_dolar
    despachante_pesos = despachante * precio_dolar
    costo_total_pesos = cif_pesos + ddi_pesos + tasas_pesos + agente_pesos + despachante_pesos  # Solo costos no recuperables
    precio_unitario_pesos = costo_unitario_usd * precio_dolar  # Convertir el precio unitario USD a pesos

    # Información del contenedor
    st.markdown("""
    <div style="width: 100%; background: linear-gradient(135deg, #FFE600 0%, #FFF533 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="color: #333333; font-size: 1.3rem; font-weight: 700; text-align: center;">🚢 Información del Contenedor</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_cont1, col_cont2, col_cont3, col_cont4 = st.columns(4)
    
    with col_cont1:
        st.markdown(f"""
        <div class="container-info">
            <h4>📦 Cajas por Contenedor</h4>
            <div style="font-size: 2rem; font-weight: bold; color: #333333;">{cajas_por_contenedor:,}</div>
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">caben en 1 contenedor</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_cont2:
        st.markdown(f"""
        <div class="container-info">
            <h4>🔢 Piezas por Contenedor</h4>
            <div style="font-size: 2rem; font-weight: bold; color: #333333;">{piezas_por_contenedor:,}</div>
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">caben en 1 contenedor</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_cont3:
        st.markdown(f"""
        <div class="container-info">
            <h4>📊 Cajas Necesarias</h4>
            <div style="font-size: 2rem; font-weight: bold; color: #333333;">{cajas_necesarias:,.0f}</div>
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">para {cantidad:,} piezas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_cont4:
        st.markdown(f"""
        <div class="container-info">
            <h4>🚢 Contenedores Necesarios</h4>
            <div style="font-size: 2rem; font-weight: bold; color: #333333;">{contenedores_necesarios:.2f}</div>
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">contenedores 40HQ</div>
        </div>
        """, unsafe_allow_html=True)

    # Resultados principales
    st.markdown("""
    <div style="width: 100%; background: linear-gradient(135deg, #FFE600 0%, #FFF533 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="color: #333333; font-size: 1.3rem; font-weight: 700; text-align: center;">🎯 Resultados Principales</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    
    with col_res1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Precio Unitario Final</div>
            <div class="result-value">${precio_unitario_usd:,.3f}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">USD por pieza</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_res2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Precio Unitario Final</div>
            <div class="result-value">${precio_unitario_pesos:,.2f}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">Pesos por pieza</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_res3:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">CBM Total</div>
            <div class="result-value">{cbm_total:.4f}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">m³</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_res4:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Costo Total</div>
            <div class="result-value">${costo_total_usd:,.2f}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">USD</div>
        </div>
        """, unsafe_allow_html=True)

    # Desglose detallado de costos
    st.markdown("""
    <div style="width: 100%; background: linear-gradient(135deg, #FFE600 0%, #FFF533 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="color: #333333; font-size: 1.3rem; font-weight: 700; text-align: center;">📋 Desglose Detallado de Costos</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_det1, col_det2 = st.columns(2)
    
    with col_det1:
        st.markdown("### 💰 Costos en USD")
        costos_usd = {
            "FOB": fob,
            "Seguro": seguro,
            "CIF": cif,
            "DDI": ddi,
            "Tasas": tasas,
            "IVA": iva,
            "IVA Adicional": iva_adic,
            "Ganancias": ganancias,
            "IIBB": iibb,
            "Agente": agente,
            "Despachante": despachante,
            "**TOTAL**": costo_total_usd
        }
        
        for concepto, valor in costos_usd.items():
            if concepto == "**TOTAL**":
                st.markdown(f"**{concepto}**: ${valor:,.2f}")
            else:
                st.write(f"{concepto}: ${valor:,.2f}")
    
    with col_det2:
        st.markdown("### 💵 Costos en Pesos")
        costos_pesos = {
            "FOB": fob_pesos,
            "Seguro": seguro_pesos,
            "CIF": cif_pesos,
            "DDI": ddi_pesos,
            "Tasas": tasas_pesos,
            "IVA": iva_pesos,
            "IVA Adicional": iva_adic_pesos,
            "Ganancias": ganancias_pesos,
            "IIBB": iibb_pesos,
            "Agente": agente_pesos,
            "Despachante": despachante_pesos,
            "**TOTAL**": costo_total_pesos
        }
        
        for concepto, valor in costos_pesos.items():
            if concepto == "**TOTAL**":
                st.markdown(f"**{concepto}**: ${valor:,.2f}")
            else:
                st.write(f"{concepto}: ${valor:,.2f}")



    # Botón para agregar producto al contenedor
    st.markdown("""
    <div style="width: 100%; background: linear-gradient(135deg, #FFE600 0%, #FFF533 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="color: #333333; font-size: 1.3rem; font-weight: 700; text-align: center;">📦 Agregar al Contenedor</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_add1, col_add2, col_add3 = st.columns([1, 2, 1])
    with col_add2:
        if st.button("➕ Agregar producto al contenedor", type="primary", use_container_width=True):
            # Agregar el producto actual al contenedor con todos los campos necesarios
            producto_para_contenedor = {
                'Nombre': nombre,
                'Precio FOB (USD)': precio_u,
                'Precio Final (USD)': precio_unitario_usd,
                'Precio Final (Pesos)': precio_unitario_pesos,
                'CBM por Caja': cbm,
                'Piezas por Caja': pcs_ctn,
                'Cajas por Contenedor': cajas_por_contenedor,
                'Piezas por Contenedor': piezas_por_contenedor,
                'Contenedores Necesarios': contenedores_necesarios,
                'CBM Total': cbm_total,
                'Peso por Caja (kg)': peso,
                'Peso Total (kg)': peso_total,
                'Cantidad Total': cantidad,
                'Costo Total (USD)': costo_total_usd,
                'Costo Total (Pesos)': costo_total_pesos,
                'Flete por Producto (USD)': 0,  # Sin flete en análisis individual
                'Gastos Fijos por Producto (USD)': 0,  # Sin gastos fijos en análisis individual
                'Largo (cm)': largo,
                'Ancho (cm)': ancho,
                'Alto (cm)': alto,
                'DDI (%)': ddi_pct,  # Agregar DDI (%) para cálculos en contenedor
                'Antidumping (USD)': 0,  # Agregar campo antidumping
            }
            
            # Validar que todos los campos numéricos tengan valores válidos
            campos_requeridos = ['Precio FOB (USD)', 'Cantidad Total', 'CBM Total', 'Peso Total (kg)']
            for campo in campos_requeridos:
                if campo not in producto_para_contenedor or producto_para_contenedor[campo] is None:
                    producto_para_contenedor[campo] = 0
            
            st.session_state['productos'].append(producto_para_contenedor)
            
            # Guardar en CSV
            if st.session_state['productos']:
                df = pd.DataFrame(st.session_state['productos'])
                df.to_csv('productos_guardados.csv', index=False)
            else:
                # Si no hay productos, eliminar el archivo si existe
                if os.path.exists('productos_guardados.csv'):
                    os.remove('productos_guardados.csv')
            
            st.markdown("""
            <div class="success-box" style="text-align: center;">
                <h3 style="margin-bottom: 1rem; font-size: 1.5rem;">✅ ¡Producto agregado exitosamente!</h3>
                <p style="margin-bottom: 1rem; font-size: 1.1rem; line-height: 1.6;">
                    El producto ha sido agregado al contenedor. Ve a "Contenedor Completo" para ver el análisis completo.
                </p>
                <p style="font-size: 1rem; opacity: 0.9;">
                    <strong>📦 Productos en contenedor:</strong> {len}
                </p>
            </div>
            """.format(len=len(st.session_state['productos'])), unsafe_allow_html=True)
            # Resetear campos después de agregar producto
            for key in [
                'Nombre del Producto', 'Precio Unitario FOB (USD)', 'Cantidad Total', 'Piezas por Caja',
                'Peso por Caja (kg)', 'Largo (cm)', 'Ancho (cm)', 'Alto (cm)'
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state['calcular'] = False
            st.rerun()

# Mensaje inicial cuando no se ha calculado
if not calcular:
    st.markdown("""
    <div class="info-box" style="text-align: center;">
        <h3 style="margin-bottom: 1rem; font-size: 1.5rem;">🚀 ¡Comienza tu análisis!</h3>
        <p style="margin-bottom: 1rem; font-size: 1.1rem; line-height: 1.6;">
            Ingresa la información del producto y haz clic en "Calcular Costos Completos" para ver el análisis detallado.
        </p>
        <p style="font-size: 1rem; opacity: 0.9; line-height: 1.5;">
            <strong>💡 Tip:</strong> Para análisis de contenedores completos con múltiples productos, usa el módulo "Contenedor Completo".
        </p>
    </div>
    """, unsafe_allow_html=True) 