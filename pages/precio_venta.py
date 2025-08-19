import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io
import tempfile

# Configuración de la página
st.set_page_config(
    page_title="💰 Análisis de Ganancias - MercadoLibre",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para una interfaz moderna
st.markdown("""
<style>
    /* Variables CSS - Colores de MercadoLibre */
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
        --primary-color: var(--ml-yellow);
        --secondary-color: var(--ml-blue);
        --accent-color: var(--ml-orange);
        --success-color: var(--ml-green);
        --warning-color: var(--ml-orange);
        --error-color: var(--ml-red);
        --text-primary: var(--ml-gray-dark);
        --text-secondary: var(--ml-gray-medium);
        --bg-primary: var(--ml-white);
        --bg-secondary: var(--ml-gray-very-light);
        --border-color: #DDDDDD;
        --shadow: 0 2px 10px rgba(0,0,0,0.1);
        --border-radius: 12px;
    }
    
    /* Estilos generales */
    .main {
        background: var(--ml-white);
        min-height: 100vh;
    }

    .stApp {
        background: var(--ml-white);
    }

    /* Header personalizado */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: var(--border-radius);
    padding: 2rem;
    margin-bottom: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--ml-blue), var(--ml-blue-dark));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    text-align: center;
        margin-bottom: 1rem;
    }

    .header-subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Navegación moderna */
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .nav-button {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid transparent;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        color: var(--text-primary);
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
        cursor: pointer;
    }
    
    .nav-button:hover {
        background: var(--ml-blue);
    color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(52, 131, 250, 0.3);
    }

    /* Uploader moderno */
    .uploader-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
        border: 2px dashed var(--ml-blue);
        text-align: center;
        transition: all 0.3s ease;
    }

    .uploader-container:hover {
        border-color: var(--ml-yellow);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(52, 131, 250, 0.2);
    }

    /* Métricas modernas */
    .metrics-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }

    .metric-card {
        background: linear-gradient(135deg, var(--ml-blue), var(--ml-blue-dark));
    color: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
    text-align: center;
        box-shadow: var(--shadow);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Tabla moderna */
    .table-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }

    /* Botones modernos */
    .stButton > button {
        background: linear-gradient(135deg, var(--ml-blue), var(--ml-blue-dark));
    color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(52, 131, 250, 0.3);
    }

    /* Mensajes de estado */
    .success-message {
        background: linear-gradient(135deg, var(--ml-green), #27AE60);
    color: white;
    padding: 1rem;
        border-radius: var(--border-radius);
    margin: 1rem 0;
        text-align: center;
        font-weight: 600;
}

    .info-message {
        background: linear-gradient(135deg, var(--ml-blue), var(--ml-blue-dark));
    color: white;
    padding: 1rem;
        border-radius: var(--border-radius);
    margin: 1rem 0;
        text-align: center;
        font-weight: 600;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        
        .nav-container {
            flex-direction: column;
        }
}
    
    /* Títulos de sección modernos */
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
    
    .section-header p {
        color: var(--text-secondary);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* KPI Cards modernos */
    .kpi-header {
        background: linear-gradient(135deg, var(--ml-blue) 0%, var(--ml-blue-light) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 5px 15px rgba(52, 131, 250, 0.2);
    }
    
    .kpi-header h3 {
        color: white;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .kpi-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin: 0;
    }
    
    /* Result Cards modernos */
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
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
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
    
    .result-label {
        font-size: 0.9rem;
        color: var(--text-light);
        margin-bottom: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .result-value {
        font-size: 1.8rem;
        font-weight: 900;
        color: var(--text-dark);
        margin-bottom: 0.3rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header principal
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
    if st.button("💰 Ganancias", key="nav-calculator", use_container_width=True, type="primary"):
        st.switch_page("pages/precio_venta.py")
with col4:
    if st.button("📋 Inventario", key="nav-inventory", use_container_width=True):
        st.switch_page("pages/inventario.py")
with col5:
    if st.button("🚀 ML Pro", key="nav-precio-ml-pro", use_container_width=True):
        st.switch_page("pages/precio_venta_ml_avanzado.py")

st.markdown("""
<div class="section-header">
    <h2>💰 Análisis de Ganancias</h2>
    <p>Procesa tus reportes de MercadoLibre y calcula tus ganancias netas</p>
</div>
""", unsafe_allow_html=True)



import tempfile
import os
import hashlib
import json

# Crear directorio para archivos persistentes
PERSISTENT_FILES_DIR = "persistent_files"
if not os.path.exists(PERSISTENT_FILES_DIR):
    os.makedirs(PERSISTENT_FILES_DIR)

# Archivo JSON para almacenar metadatos
METADATA_FILE = os.path.join(PERSISTENT_FILES_DIR, "uploaded_files_metadata.json")

# Inicializar session_state para archivos cargados
if 'uploaded_files_metadata' not in st.session_state:
    # Cargar metadatos desde archivo JSON
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                data = json.load(f)
                # Validar que sea una lista
                if isinstance(data, list):
                    # Filtrar solo elementos que sean diccionarios válidos
                    valid_metadata = []
                    for item in data:
                        if isinstance(item, dict) and 'name' in item:
                            valid_metadata.append(item)
                    st.session_state['uploaded_files_metadata'] = valid_metadata
                else:
                    st.session_state['uploaded_files_metadata'] = []
        except (json.JSONDecodeError, FileNotFoundError):
            st.session_state['uploaded_files_metadata'] = []
    else:
        st.session_state['uploaded_files_metadata'] = []

if 'uploaded_product_costs_metadata' not in st.session_state:
    # Cargar metadatos de costos desde archivo JSON
    costs_metadata_file = os.path.join(PERSISTENT_FILES_DIR, "product_costs_metadata.json")
    if os.path.exists(costs_metadata_file):
        try:
            with open(costs_metadata_file, 'r') as f:
                st.session_state['uploaded_product_costs_metadata'] = json.load(f)
        except:
            st.session_state['uploaded_product_costs_metadata'] = None
    else:
        st.session_state['uploaded_product_costs_metadata'] = None

# Función para guardar metadatos en archivo JSON
def save_gastos_trabajo():
    """Guardar gastos de trabajo en archivo JSON"""
    gastos_file = "gastos_trabajo.json"
    gastos_data = {
        'lista_gastos': st.session_state.get('lista_gastos', []),
        'total': st.session_state.get('gastos_trabajo', 0.0)
    }
    with open(gastos_file, 'w') as f:
        json.dump(gastos_data, f, indent=2)

def save_metadata_to_file():
    """Guarda los metadatos en archivos JSON para persistencia"""
    try:
        # Guardar metadatos de archivos principales
        with open(METADATA_FILE, 'w') as f:
            json.dump(st.session_state['uploaded_files_metadata'], f)
        
        # Guardar metadatos de archivo de costos
        costs_metadata_file = os.path.join(PERSISTENT_FILES_DIR, "product_costs_metadata.json")
        with open(costs_metadata_file, 'w') as f:
            json.dump(st.session_state['uploaded_product_costs_metadata'], f)
        
        return True
    except Exception as e:
        st.error(f"Error al guardar metadatos: {e}")
        return False

# Función para guardar archivo persistentemente
def save_uploaded_file(uploaded_file, file_type="mercadolibre"):
    """Guarda un archivo subido en el directorio persistente y retorna metadatos"""
    if uploaded_file is None:
        return None
    
    # Crear hash único para el archivo
    file_content = uploaded_file.read()
    uploaded_file.seek(0)
    file_hash = hashlib.md5(file_content).hexdigest()
    
    # Crear nombre de archivo persistente
    safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in ('.-_')).rstrip()
    persistent_filename = f"{file_type}_{file_hash}_{safe_filename}"
    persistent_filepath = os.path.join(PERSISTENT_FILES_DIR, persistent_filename)
    
    # Guardar archivo persistentemente
    with open(persistent_filepath, 'wb') as f:
        f.write(file_content)
    
    # Retornar metadatos
    return {
        'name': uploaded_file.name,
        'type': uploaded_file.type,
        'size': uploaded_file.size,
        'persistent_path': persistent_filepath,
        'hash': file_hash
    }

# Función para cargar archivo desde metadatos
def load_file_from_metadata(metadata):
    """Carga un archivo desde sus metadatos guardados"""
    if metadata is None or not os.path.exists(metadata['persistent_path']):
        return None
    
    # Crear un objeto similar a UploadedFile
    class PersistentUploadedFile:
        def __init__(self, metadata):
            self.name = metadata['name']
            self.type = metadata['type']
            self.size = metadata['size']
            self.persistent_path = metadata['persistent_path']
        
        def read(self):
            with open(self.persistent_path, 'rb') as f:
                return f.read()
        
        def seek(self, position):
            pass  # No es necesario para archivos persistentes
        
        def __str__(self):
            return self.persistent_path
        
        def __fspath__(self):
            return self.persistent_path
    
    return PersistentUploadedFile(metadata)

# Sidebar solo con uploaders
with st.sidebar:

    
    # Uploader principal para reporte de MercadoLibre
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
        <h5 style="color: var(--ml-blue); margin: 0; font-size: 1rem;">📊 Reportes MercadoLibre</h5>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Seleccionar reportes (puedes cargar varios)",
        type=["csv", "xlsx", "xls"],
        key="mercadolibre_uploader",
        label_visibility="collapsed",
        accept_multiple_files=True
    )
    
    # Procesar nuevos archivos y guardarlos
    if uploaded_files:
        new_files_metadata = []
        for file in uploaded_files:
            # Verificar si el archivo ya está guardado
            file_content = file.read()
            file.seek(0)
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Buscar si ya existe
            exists = False
            for existing_metadata in st.session_state['uploaded_files_metadata']:
                if existing_metadata['hash'] == file_hash:
                    exists = True
                    break
            
            if not exists:
                # Guardar nuevo archivo
                metadata = save_uploaded_file(file, "mercadolibre")
                if metadata:
                    new_files_metadata.append(metadata)
        
        # Agregar nuevos archivos al session_state
        if new_files_metadata:
            st.session_state['uploaded_files_metadata'].extend(new_files_metadata)
            save_metadata_to_file()  # Guardar metadatos persistentemente
            st.success(f"✅ {len(new_files_metadata)} nuevo(s) archivo(s) cargado(s)")
    
    # Mostrar archivos cargados persistentemente
    if st.session_state['uploaded_files_metadata']:
        with st.expander("📁 Archivos cargados", expanded=False):
            for i, metadata in enumerate(st.session_state['uploaded_files_metadata']):
                # Validar que metadata sea un diccionario válido
                if isinstance(metadata, dict) and 'name' in metadata:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {metadata['name']}")
                    with col2:
                        if st.button("🗑️", key=f"del_file_{i}", help=f"Eliminar {metadata['name']}"):
                            # Eliminar archivo persistente
                            if 'persistent_path' in metadata and os.path.exists(metadata['persistent_path']):
                                os.remove(metadata['persistent_path'])
                            # Eliminar de session_state
                            st.session_state['uploaded_files_metadata'].pop(i)
                            save_metadata_to_file()  # Guardar metadatos persistentemente
                            st.rerun()
                else:
                    # Si el metadata no es válido, eliminarlo
                    st.session_state['uploaded_files_metadata'].pop(i)
                    save_metadata_to_file()
                    st.rerun()
    
    # Uploader de costos por producto
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
        <h5 style="color: var(--ml-blue); margin: 0; font-size: 1rem;">📦 Costos por Producto</h5>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_product_costs_file = st.file_uploader(
        "Seleccionar archivo de costos por producto",
        type=["xlsx", "xls"],
        key="product_costs_uploader",
        label_visibility="collapsed"
    )
    
    # Procesar archivo de costos por producto
    if uploaded_product_costs_file is not None:
        # Verificar si es un archivo nuevo
        file_content = uploaded_product_costs_file.read()
        uploaded_product_costs_file.seek(0)
        file_hash = hashlib.md5(file_content).hexdigest()
        
        # Solo guardar si es diferente al actual
        if (st.session_state['uploaded_product_costs_metadata'] is None or 
            st.session_state['uploaded_product_costs_metadata']['hash'] != file_hash):
            metadata = save_uploaded_file(uploaded_product_costs_file, "costs")
            if metadata:
                st.session_state['uploaded_product_costs_metadata'] = metadata
                save_metadata_to_file()  # Guardar metadatos persistentemente
                st.success("✅ Costos por producto cargados")
    
    # Mostrar archivo de costos cargado persistentemente
    if st.session_state['uploaded_product_costs_metadata'] is not None:
        with st.expander("💰 Archivo de costos cargado", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {st.session_state['uploaded_product_costs_metadata']['name']}")
            with col2:
                if st.button("🗑️", key="del_costs_file", help="Eliminar archivo de costos"):
                    # Eliminar archivo persistente
                    if os.path.exists(st.session_state['uploaded_product_costs_metadata']['persistent_path']):
                        os.remove(st.session_state['uploaded_product_costs_metadata']['persistent_path'])
                    # Eliminar de session_state
                    st.session_state['uploaded_product_costs_metadata'] = None
                    save_metadata_to_file()  # Guardar metadatos persistentemente
                    st.rerun()
    
    # Configuración de visualización
    st.markdown("**⚙️ Configuración de Visualización**")
    
    # Inicializar configuración de visualización
    if 'show_individual_analysis' not in st.session_state:
        st.session_state['show_individual_analysis'] = False
    
    # Toggle para mostrar/ocultar análisis individuales
    show_individual = st.checkbox(
        "📊 Mostrar análisis individuales",
        value=st.session_state['show_individual_analysis'],
        help="Activa para ver las tablas de ventas procesadas, costos por producto y costos de operación"
    )
    
    # Actualizar session_state
    if show_individual != st.session_state['show_individual_analysis']:
        st.session_state['show_individual_analysis'] = show_individual
    


# Usar archivos del session_state para procesamiento
files_to_process = []
for metadata in st.session_state['uploaded_files_metadata']:
    file_obj = load_file_from_metadata(metadata)
    if file_obj:
        files_to_process.append(file_obj)

product_costs_to_process = None
if st.session_state['uploaded_product_costs_metadata']:
    product_costs_to_process = load_file_from_metadata(st.session_state['uploaded_product_costs_metadata'])

if files_to_process:
    # Procesar múltiples archivos
    all_processed_data = []
    
    for uploaded_file in files_to_process:
        try:
            # Detectar el tipo de archivo
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            # Leer el archivo según su tipo
            if file_extension in ['xlsx', 'xls']:
                # Leer archivo Excel
                try:
                    df = pd.read_excel(uploaded_file, header=None)
                except Exception as e:
                    st.error(f"❌ Error al leer archivo Excel: {e}")
                    continue
            else:
                # Leer archivo CSV
                content = uploaded_file.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                uploaded_file.seek(0)
                
                # Procesar el archivo línea por línea
                lines = content.split('\n')
                
                # Buscar la línea de encabezados
                header_row = None
                for i, line in enumerate(lines):
                    if line.strip() and ('Número de venta' in line or 'N° de factura fiscal' in line):
                        header_row = i
                        break
                
                if header_row is None:
                    st.error("❌ No se encontraron encabezados válidos en el archivo")
                    continue
                
                # Verificar que hay suficientes líneas después del header
                if header_row >= len(lines) - 1:
                    st.error("❌ No hay datos después de los encabezados")
                    continue
                
                # Leer el archivo con pandas usando la fila de encabezados encontrada
                try:
                    df = pd.read_csv(uploaded_file, header=header_row)
                except Exception as e:
                    try:
                        df = pd.read_csv(uploaded_file, header=None)
                        
                        # Buscar manualmente la fila con encabezados
                        header_found = False
                        for i in range(len(df)):
                            row = df.iloc[i]
                            row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                            if 'Número de venta' in row_str or 'N° de factura fiscal' in row_str:
                                df.columns = df.iloc[i]
                                df = df.iloc[i+1:].reset_index(drop=True)
                                header_found = True
                                break
                        
                        if not header_found:
                            st.error("❌ No se encontraron encabezados en el archivo")
                            continue
                    except Exception as e2:
                        # Intentar con diferentes delimitadores y encodings
                        for delimiter in [',', ';', '\t']:
                            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                                try:
                                    uploaded_file.seek(0)
                                    df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding, header=None)
                                    
                                    # Buscar encabezados
                                    header_found = False
                                    for i in range(len(df)):
                                        row = df.iloc[i]
                                        row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                                        if 'Número de venta' in row_str or 'N° de factura fiscal' in row_str:
                                            df.columns = df.iloc[i]
                                            df = df.iloc[i+1:].reset_index(drop=True)
                                            header_found = True
                                            break
                                    
                                    if header_found:
                                        break
                                except:
                                    continue
                            
                            if header_found:
                                break
                        
                        if not header_found:
                            st.error("❌ No se pudo leer el archivo")
                            continue
            
            # Para archivos Excel, buscar encabezados manualmente
            if file_extension in ['xlsx', 'xls']:
                header_found = False
                for i in range(len(df)):
                    row = df.iloc[i]
                    row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                    if 'Número de venta' in row_str or 'N° de factura fiscal' in row_str:
                        df.columns = df.iloc[i]
                        df = df.iloc[i+1:].reset_index(drop=True)
                        header_found = True
                        break
                
                if not header_found:
                    st.error("❌ No se encontraron encabezados en el archivo Excel")
                    continue
            
            # Normalizar nombres de columnas
            df.columns = df.columns.str.strip().str.lower()
            
            # Buscar las columnas relevantes
            columnas_buscadas = {
                'fecha de venta': None,
                'total de la venta': None,
                'título de publicación': None,
                'número de venta': None,
                'cantidad': None  # Agregar búsqueda de cantidad
            }
            
            for col in df.columns:
                col_lower = col.lower()
                for busqueda, valor in columnas_buscadas.items():
                    if busqueda in col_lower and valor is None:
                        columnas_buscadas[busqueda] = col
            
            # Verificar que tenemos las columnas necesarias (cantidad es opcional)
            columnas_requeridas = ['fecha de venta', 'total de la venta', 'título de publicación', 'número de venta']
            if not all(columnas_buscadas[col] for col in columnas_requeridas):
                st.error("❌ Faltan columnas esenciales para el análisis")
                continue
            
            # --- Asegurar que df es DataFrame tras la carga ---
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame(df)
            # ---
            columnas_relevantes = [col for col in columnas_buscadas.values() if col]
            df_relevante = df[columnas_relevantes].copy()
            if not isinstance(df_relevante, pd.DataFrame):
                df_relevante = pd.DataFrame(df_relevante)
            # ---
            # Filtrar ventas válidas (Cobrado de la operación = SI)
            cobrado_col = None
            for col in df.columns:
                if 'cobrado de la operación' in col.lower():
                    cobrado_col = col
                    break
            ventas_validas = None
            if cobrado_col and cobrado_col in df.columns:
                ventas_validas = set(df[df[cobrado_col].astype(str).str.strip().str.upper() == 'SI'][columnas_buscadas['número de venta']].astype(str))
                ventas_validas_list = list(ventas_validas)
                df = df[df[columnas_buscadas['número de venta']].astype(str).isin(ventas_validas_list)]
            
            # Filtrar ventas canceladas (excluir estados de cancelación)
            estado_col = None
            for col in df.columns:
                if 'estado' in col.lower():
                    estado_col = col
                    break
            
            if estado_col and estado_col in df.columns:
                # Estados que indican cancelación o devolución
                estados_cancelados = [
                    'cancelado', 'cancelada', 'cancelación', 'cancelada',
                    'devuelto', 'devuelta', 'devolución', 'devoluciones',
                    'reembolsado', 'reembolso', 'reembolsada',
                    'anulado', 'anulada', 'anulación',
                    'rechazado', 'rechazada', 'rechazo'
                ]
                
                # Filtrar ventas que NO estén en estados cancelados
                df = df[~df[estado_col].astype(str).str.lower().isin(estados_cancelados)]
                
                # Mostrar estadísticas de filtrado
                total_ventas = len(df)
                ventas_canceladas = len(df[df[estado_col].astype(str).str.lower().isin(estados_cancelados)])
                if ventas_canceladas > 0:
                    st.info(f"🔄 **Filtrado automático:** Se excluyeron {ventas_canceladas} ventas canceladas/devueltas")
            
            # Aplicar el mismo filtro de ventas válidas al DataFrame relevante
            df_relevante = df_relevante[df_relevante[columnas_buscadas['número de venta']].astype(str).isin(ventas_validas_list)]
            
            # Aplicar el mismo filtro de estados cancelados al DataFrame relevante
            if estado_col and estado_col in df_relevante.columns:
                df_relevante = df_relevante[~df_relevante[estado_col].astype(str).str.lower().isin(estados_cancelados)]
            
            # Limpiar datos
            numero_venta_col = columnas_buscadas['número de venta']
            if numero_venta_col and isinstance(numero_venta_col, str) and isinstance(df_relevante, pd.DataFrame) and numero_venta_col in df_relevante.columns:
                df_relevante = df_relevante.dropna(subset=[numero_venta_col])
            else:
                st.error(f"❌ Columna de número de venta '{numero_venta_col}' no encontrada en el DataFrame")
                continue
            
            # Función para limpiar números con formato argentino (comas como separadores de miles)
            def limpiar_numero_argentino(valor):
                if pd.isna(valor) or valor == '':
                    return 0.0
                try:
                    # Convertir a string y limpiar
                    valor_str = str(valor).strip()
                    # Remover comillas dobles si existen
                    valor_str = valor_str.replace('"', '')
                    # Remover comas (separadores de miles) y convertir a float
                    valor_limpio = valor_str.replace(',', '')
                    return float(valor_limpio)
                except Exception as e:
                    # Debug: mostrar el valor que no se pudo convertir
                    print(f"Error convirtiendo valor: '{valor}' - Error: {e}")
                    return 0.0
            
            # Limpiar y convertir a número la columna 'Total de la venta' antes de agrupar
            if columnas_buscadas['total de la venta'] in df_relevante.columns:
                df_relevante[columnas_buscadas['total de la venta']] = df_relevante[columnas_buscadas['total de la venta']].apply(limpiar_numero_argentino)
            # ---
            # Agrupar por número de venta y tomar el primer valor de 'Total de la venta' (no sumarlo)
            numero_venta_col = columnas_buscadas['número de venta']
            if numero_venta_col and isinstance(numero_venta_col, str) and numero_venta_col in df_relevante.columns:
                columnas_agrupar = [numero_venta_col]
                columnas_primero = []
                if columnas_buscadas['fecha de venta'] in df_relevante.columns:
                    columnas_primero.append(columnas_buscadas['fecha de venta'])
                if columnas_buscadas['título de publicación'] in df_relevante.columns:
                    columnas_primero.append(columnas_buscadas['título de publicación'])
                if columnas_buscadas['cantidad'] and columnas_buscadas['cantidad'] in df_relevante.columns:
                    columnas_primero.append(columnas_buscadas['cantidad'])
                # Realizar agrupación
                ventas_unicas = df_relevante.groupby(columnas_agrupar).agg({
                    columnas_buscadas['total de la venta']: 'first',  # Tomar el primer valor, no sumar
                    **{col: 'first' for col in columnas_primero}
                }).reset_index()
            else:
                st.error("❌ Error en la agrupación de ventas")
                continue
            
            # Renombrar columnas para mayor claridad
            ventas_unicas_renombradas = ventas_unicas.rename(columns={
                columnas_buscadas['número de venta']: 'Número de venta',
                columnas_buscadas['total de la venta']: 'Total de la venta',
                columnas_buscadas['fecha de venta']: 'Fecha de venta',
                columnas_buscadas['título de publicación']: 'Título de publicación'
            })
            
            # Agregar columna de cantidad si existe
            if columnas_buscadas['cantidad'] and columnas_buscadas['cantidad'] in ventas_unicas.columns:
                ventas_unicas_renombradas['Cantidad'] = ventas_unicas[columnas_buscadas['cantidad']]
            else:
                ventas_unicas_renombradas['Cantidad'] = 1
            
            # Agregar información del archivo
            ventas_unicas_renombradas['Archivo'] = uploaded_file.name
            ventas_unicas_renombradas['Mes'] = uploaded_file.name.split('_')[0] if '_' in uploaded_file.name else 'Sin mes'
            
            # Guardar datos procesados
            all_processed_data.append(ventas_unicas_renombradas)
            
        except Exception as e:
            st.error(f"❌ Error en {uploaded_file.name}: {e}")
            continue
    
            # Combinar todos los datos procesados
        if all_processed_data:
            # Combinar todos los DataFrames
            if len(all_processed_data) > 1:
                ventas_unicas_renombradas = pd.concat(all_processed_data, ignore_index=True)
            else:
                ventas_unicas_renombradas = all_processed_data[0]
        
        # Guardar en session state para uso posterior
        st.session_state['ventas_unicas'] = ventas_unicas_renombradas
        st.session_state['columnas_originales'] = columnas_buscadas
        
        # Formatear fecha de venta (eliminar hora)
        if 'Fecha de venta' in ventas_unicas_renombradas.columns:
            try:
                ventas_unicas_renombradas['Fecha de venta'] = pd.to_datetime(ventas_unicas_renombradas['Fecha de venta']).dt.strftime('%d/%m/%Y')
            except:
                pass
        
        # Agregar columna de sumatoria con limpieza de números
        if 'Total de la venta' in ventas_unicas_renombradas.columns:
            ventas_unicas_renombradas['Total de la venta'] = ventas_unicas_renombradas['Total de la venta'].apply(limpiar_numero_argentino)
        
        # --- TABLA DE VENTAS (DESPLEGABLE) ---
        if st.session_state.get('show_individual_analysis', False):
            with st.expander("📊 Ventas Procesadas", expanded=False):
                st.dataframe(ventas_unicas_renombradas, use_container_width=True)
        
                # --- GENERAR ARCHIVO DE COSTOS POR PRODUCTO (DESPLEGABLE) ---
        if st.session_state.get('show_individual_analysis', False):
            with st.expander("📋 Generar Plantilla de Costos por Producto", expanded=False):
                if 'Título de publicación' in ventas_unicas_renombradas.columns:
                    # Obtener títulos únicos de productos
                    productos_unicos = ventas_unicas_renombradas['Título de publicación'].dropna().unique()
                    
                    # Crear DataFrame para costos por producto
                    df_costos_producto = pd.DataFrame({
                        'SKU': [f'SKU_{i+1:04d}' for i in range(len(productos_unicos))],
                        'Título de la publicación': productos_unicos,
                        'Costo unitario': 0.0,
                        'Notas': ''
                    })
                    
                    # Sección mejorada para generar archivo de costos por producto
                    st.markdown("""
                    <div class="kpi-header">
                        <h3>📋 Generar Plantilla de Costos por Producto</h3>
                        <p>Descarga la plantilla Excel con todos los productos únicos. Incluye SKU automático y campos para agregar costos manualmente</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Convertir DataFrame a Excel usando archivo temporal
                    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                        df_costos_producto.to_excel(tmp_file.name, sheet_name='Costos por Producto', index=False)
                        with open(tmp_file.name, 'rb') as f:
                            excel_data = f.read()
                    
                    # Botón de descarga mejorado
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        import uuid
                        unique_key = f"download_costos_template_{uuid.uuid4().hex[:8]}"
                        st.download_button(
                            label="📥 Descargar Plantilla de Costos",
                            data=excel_data,
                            file_name=f"costos_productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key=unique_key
                        )
                    
                    st.markdown(f"""
                    <div class="info-card">
                        📊 Se encontraron <strong>{len(productos_unicos)} productos únicos</strong>. 
                        Completa los costos unitarios en la plantilla descargada.
                    </div>
                    """, unsafe_allow_html=True)
        
        # Procesar archivo de costos por producto
        if product_costs_to_process is not None:
            try:
                # Detectar el tipo de archivo
                product_costs_extension = product_costs_to_process.name.lower().split('.')[-1]
                
                if product_costs_extension in ['xlsx', 'xls']:
                    df_product_costs = pd.read_excel(product_costs_to_process)
                else:
                    df_product_costs = pd.read_csv(product_costs_to_process)
                
                # Normalizar nombres de columnas
                df_product_costs.columns = df_product_costs.columns.str.strip()
                
                # Buscar columna de costo flexible
                costo_col = None
                variantes_costo = ['Costo unitario', 'Costo_Producto_sin_IVA', 'Costo', 'Precio', 'Valor']
                for variante in variantes_costo:
                    if variante in df_product_costs.columns:
                        costo_col = variante
                        break
                
                if not costo_col:
                    st.error(f"❌ No se encontró columna de costo. Columnas disponibles: {list(df_product_costs.columns)}")
                    st.error("El archivo debe contener una columna de costo con alguno de estos nombres: 'Costo unitario', 'Costo_Producto_sin_IVA', 'Costo', 'Precio', 'Valor'")
                    st.stop()
                
                # Limpiar datos
                df_product_costs = df_product_costs.dropna(subset=['Título de la publicación'])
                df_product_costs[costo_col] = df_product_costs[costo_col].fillna(0)
                
                # Convertir costos a números
                def limpiar_costo(valor):
                    if pd.isna(valor) or valor == '':
                        return 0.0
                    try:
                        if isinstance(valor, str):
                            valor = valor.replace('$', '').replace(',', '').strip()
                        return float(valor)
                    except:
                        return 0.0
                
                df_product_costs[costo_col] = df_product_costs[costo_col].apply(limpiar_costo)
                
                # Crear diccionario de costos por producto en USD
                costos_por_producto = {}
                
                for _, row in df_product_costs.iterrows():
                    titulo = str(row['Título de la publicación'])
                    costo_usd = row[costo_col]
                    
                    # Guardar el costo en USD directamente
                    costos_por_producto[titulo] = float(costo_usd)
                
                # --- TABLA DE COSTOS POR PRODUCTO (DESPLEGABLE) ---
                if st.session_state.get('show_individual_analysis', False):
                    with st.expander("📦 Costos por Producto", expanded=False):
                        st.dataframe(df_product_costs, use_container_width=True)
                
                # Guardar en session state
                st.session_state['costos_por_producto'] = costos_por_producto
                
            except Exception as e:
                st.error(f"❌ Error al procesar archivo de costos por producto: {e}")
        
        # Procesar costos de todos los archivos de MercadoLibre
        all_costs_data = []
        
        for uploaded_file in files_to_process:
            try:
                
                # Detectar el tipo de archivo
                costs_file_extension = uploaded_file.name.lower().split('.')[-1]
                if costs_file_extension in ['xlsx', 'xls']:
                    df_preview = pd.read_excel(uploaded_file, header=None)
                    header_row = None
                    # Buscar más abajo en el archivo (hasta la fila 50)
                    for i, row in df_preview.head(50).iterrows():
                        row_str = ' '.join([str(cell).lower() for cell in row if pd.notna(cell)])
                        if 'número de venta' in row_str or 'numero de venta' in row_str or 'fecha de venta' in row_str:
                            header_row = i
                            break
                    if header_row is None:
                        st.error("❌ No se encontró la fila de encabezados en el archivo Excel de costos")
                        st.write(f"Primeras filas detectadas:\n{df_preview.head(20)}")
                        st.stop()
                    uploaded_file.seek(0)
                    df_costs = pd.read_excel(uploaded_file, header=header_row)
                else:
                    df_costs = pd.read_csv(uploaded_file)
                df_costs.columns = df_costs.columns.str.strip().str.lower()
                
                # Filtrar filas donde 'Cobrado de la operación' es distinto de 'NO APLICA'
                cobrado_col = None
                for col in df_costs.columns:
                    if 'cobrado de la operación' in col or 'cobrado de la operacion' in col:
                        cobrado_col = col
                        break
                if cobrado_col:
                    df_costs = df_costs[df_costs[cobrado_col].astype(str).str.strip().str.upper() != 'NO APLICA']

                # Mapeo flexible de columnas
                columnas_objetivo = {
                    'número de venta': ['número de venta', 'numero de venta'],
                    'número de paquete': ['número de paquete', 'numero de paquete'],
                    'detalle': ['detalle'],
                    'valor del cargo': ['valor del cargo']
                }
                columnas_encontradas = {}
                for objetivo, variantes in columnas_objetivo.items():
                    for variante in variantes:
                        for col in df_costs.columns:
                            if variante in col:
                                columnas_encontradas[objetivo] = col
                                break
                        if objetivo in columnas_encontradas:
                            break

                # Validar columnas clave
                if 'número de venta' not in columnas_encontradas or 'detalle' not in columnas_encontradas or 'valor del cargo' not in columnas_encontradas:
                    st.error("❌ No se encontraron las columnas clave en el archivo de costos")
                    st.write(f"Columnas detectadas: {list(df_costs.columns)}")
                    st.stop()
                venta_col = columnas_encontradas['número de venta']
                paquete_col = columnas_encontradas.get('número de paquete', None)
                detalle_col = columnas_encontradas['detalle']
                valor_col = columnas_encontradas['valor del cargo']

                # Limpiar datos de costos
                dropna_cols = [col for col in [venta_col, detalle_col, valor_col] if col in df_costs.columns]
                if isinstance(df_costs, pd.DataFrame) and dropna_cols:
                    df_costs = df_costs.dropna(subset=dropna_cols)
                # If dropna_cols is empty, skip dropna
                if isinstance(df_costs, pd.DataFrame) and venta_col in df_costs.columns:
                    df_costs = df_costs[df_costs[venta_col].astype(str).str.strip() != '']

                # Limpiar valores numéricos usando la función global limpiar_numero_argentino
                if isinstance(df_costs, pd.DataFrame) and valor_col in df_costs.columns:
                    df_costs[valor_col] = df_costs[valor_col].apply(limpiar_numero_argentino)

                # --- NUEVO: Tomar campos descriptivos ---
                # Detectar columnas descriptivas
                campos_descriptivos = {}
                for desc in ['título de publicación', 'fecha de venta']:
                    for col in df_costs.columns:
                        if desc in col:
                            campos_descriptivos[desc] = col
                            break
                # Usar SOLO número de venta para el pivot (no incluir número de paquete)
                index_cols_pivot = [venta_col]
                
                # Pivotear la columna 'detalle' para que cada tipo de cargo sea una columna
                df_pivot = df_costs.pivot_table(
                    index=index_cols_pivot,
                    columns=detalle_col,
                    values=valor_col,
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()
                
                # Para campos descriptivos, usar número de venta y paquete si existe
                if paquete_col and paquete_col in df_costs.columns:
                    index_cols_desc = [venta_col, paquete_col]
                else:
                    index_cols_desc = [venta_col]
                if campos_descriptivos:
                    df_desc = df_costs.groupby(index_cols_desc).agg({v: 'first' for v in campos_descriptivos.values()}).reset_index()
                else:
                    df_desc = None
                df_pivot.columns.name = None
                df_pivot = df_pivot.rename(columns={venta_col: 'Número de venta', paquete_col: 'Número de paquete'} if paquete_col else {venta_col: 'Número de venta'})

                # Unir campos descriptivos a la tabla final
                if df_desc is not None:
                    # Renombrar descriptivos a nombres amigables
                    rename_desc = {}
                    for k, v in campos_descriptivos.items():
                        if k == 'título de publicación':
                            rename_desc[v] = 'Título de la publicación'
                        elif k == 'fecha de venta':
                            rename_desc[v] = 'Fecha de venta'
                    df_desc = df_desc.rename(columns=rename_desc)
                    # Formatear fecha de venta sin hora
                    if 'Fecha de venta' in df_desc.columns:
                        df_desc['Fecha de venta'] = pd.to_datetime(df_desc['Fecha de venta'], errors='coerce').dt.strftime('%d/%m/%Y')
                    # Unir descriptivos usando solo las claves que existen en ambos DataFrames
                    claves_merge = [col for col in ['Número de venta', 'Número de paquete'] if col in df_pivot.columns and col in df_desc.columns]
                    if claves_merge:
                        df_pivot = pd.merge(df_pivot, df_desc, how='left', on=claves_merge)

                # Reordenar columnas: descriptivos primero, luego cargos
                cols_order = []
                for col in ['Número de venta', 'Número de paquete', 'Título de la publicación', 'Fecha de venta']:
                    if col in df_pivot.columns:
                        cols_order.append(col)
                cols_order += [col for col in df_pivot.columns if col not in cols_order]
                df_pivot = df_pivot[cols_order]

                # Excluir 'Cargo por envíos de Mercado Libre' y variantes del cálculo y del encabezado
                variantes_envio = [col for col in df_pivot.columns if 'envío' in col.lower() or 'envio' in col.lower()]
                if variantes_envio:
                    df_pivot = df_pivot.drop(columns=variantes_envio, errors='ignore')
                # Recalcular la sumatoria de costos sin esas columnas
                cols_descriptivos = ['Número de venta', 'Número de paquete', 'Título de la publicación', 'Fecha de venta']
                cols_cargos = [col for col in df_pivot.columns if col not in cols_descriptivos and col != 'Total de costos']
                if cols_cargos:
                    df_pivot['Total de costos'] = df_pivot[cols_cargos].sum(axis=1)
                else:
                    df_pivot['Total de costos'] = 0.0

                # Guardar costos procesados de este archivo
                all_costs_data.append(df_pivot)
                
            except Exception as e:
                st.error(f"❌ Error en costos: {e}")
                continue
        
        # Combinar todos los costos procesados
        if all_costs_data:
            if len(all_costs_data) > 1:
                df_pivot = pd.concat(all_costs_data, ignore_index=True)
            else:
                df_pivot = all_costs_data[0]
            
            # --- TABLA DE COSTOS DE OPERACIÓN (DESPLEGABLE) ---
            if st.session_state.get('show_individual_analysis', False):
                with st.expander("💰 Costos de Operación por Venta", expanded=False):
                    st.markdown("""
                    <p style="color: var(--text-secondary); margin-bottom: 1rem;">Costos de MercadoLibre (comisiones, cargos, etc.) excluyendo envíos</p>
                    """, unsafe_allow_html=True)
                    st.dataframe(df_pivot, use_container_width=True)
                    st.info(f"📊 Total: {len(df_pivot)} operaciones con costos")
            
            st.session_state['costos'] = df_pivot
            st.session_state['numero_venta_col_costs'] = venta_col
    
    # --- ANÁLISIS FINAL UNIFICADO ---
    # Solo ejecutar si se procesaron costos exitosamente y hay ventas
    if all_costs_data and 'ventas_unicas' in st.session_state:
        df_pivot = all_costs_data[0] if len(all_costs_data) == 1 else pd.concat(all_costs_data, ignore_index=True)
        
        # Unir ventas con costos para calcular ganancia neta
        if isinstance(df_pivot, pd.DataFrame) and 'Número de venta' in df_pivot.columns and 'Total de costos' in df_pivot.columns:
            ventas_df = st.session_state['ventas_unicas'].copy()
            # Asegurar que la columna de número de venta sea string para el merge
            ventas_df['Número de venta'] = ventas_df['Número de venta'].astype(str)
            df_pivot['Número de venta'] = df_pivot['Número de venta'].astype(str)
            
            # Limpiar formato de números de venta en df_pivot (remover .0 al final)
            df_pivot['Número de venta'] = df_pivot['Número de venta'].str.replace('.0', '', regex=False)
            
            # Usar directamente df_pivot para obtener los costos de operación
            # Crear un diccionario de costos por número de venta
            costos_dict = dict(zip(df_pivot['Número de venta'], df_pivot['Total de costos']))
            
            # Crear resultado_final con los datos de ventas
            resultado_final = ventas_df.copy()
            resultado_final['Costo por producto'] = 0.0  # Inicializar
            
            # Agregar costos de operación usando el diccionario
            def obtener_costo_operacion(numero_venta):
                return costos_dict.get(str(numero_venta), 0.0)
            
            resultado_final['Costos de operación'] = resultado_final['Número de venta'].apply(obtener_costo_operacion)
            
            # --- CALCULAR COSTOS POR PRODUCTO ---
            # Inicializar costos si no existen
            if 'costos_por_producto' not in st.session_state:
                st.session_state['costos_por_producto'] = {}
            
            # Obtener todos los productos
            todos_productos = resultado_final['Título de publicación'].unique()
            productos_sin_costo = []
            
            if st.session_state['costos_por_producto']:
                for producto in todos_productos:
                    if producto not in st.session_state['costos_por_producto']:
                        productos_sin_costo.append(producto)
            else:
                productos_sin_costo = list(todos_productos)
            
            # Sidebar para controles
            with st.sidebar:
                
                # Control de tasa de cambio para costos
                st.markdown("### 💱 Tasa de Cambio USD → ARS")
                
                # Inicializar tasa de cambio en session state
                if 'tasa_cambio_actual' not in st.session_state:
                    st.session_state['tasa_cambio_actual'] = 1350.0  # Tasa estándar
                
                # Input para tasa de cambio (reactivo)
                tasa_actual = st.number_input(
                    "Tasa USD → ARS:",
                    min_value=0.1,
                    max_value=10000.0,
                    value=st.session_state.get('tasa_cambio_actual', 1350.0),
                    step=0.01,
                    help="Tasa de conversión de dólares a pesos argentinos",
                    key="tasa_input"
                )
                
                # Actualizar session state automáticamente
                st.session_state['tasa_cambio_actual'] = tasa_actual
                
                if len(productos_sin_costo) > 0:
                    st.markdown("### 📥 Descargar Plantillas")
                    
                    # Botón para plantilla completa
                    df_plantilla_completa = pd.DataFrame([
                        {'Título de la publicación': producto, 'Costo unitario': 0}
                        for producto in todos_productos
                    ])
                    
                    output_completa = io.BytesIO()
                    with pd.ExcelWriter(output_completa, engine='openpyxl') as writer:
                        df_plantilla_completa.to_excel(writer, sheet_name='Costos_Productos', index=False)
                    excel_data_completa = output_completa.getvalue()
                    
                    st.download_button(
                        label="📥 Plantilla Completa",
                        data=excel_data_completa,
                        file_name=f"plantilla_costos_completa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="sidebar_download_completa"
                    )
                    

                    


            # --- CALCULAR COSTOS POR PRODUCTO (DESPUÉS DE AGREGAR) ---
            if st.session_state['costos_por_producto']:
                costos_producto = st.session_state['costos_por_producto']
                
                # Calcular costo por producto basado en título y cantidad
                def calcular_costo_producto(row):
                    # Buscar la columna de título de manera flexible
                    titulo_col = None
                    for col in row.index:
                        if 'título' in col.lower() and 'publicación' in col.lower():
                            titulo_col = col
                            break
                    
                    if titulo_col and titulo_col in row.index:
                        titulo = str(row[titulo_col]) if pd.notna(row[titulo_col]) else ''
                    else:
                        # Si no encuentra la columna, intentar con 'Título de publicación'
                        titulo = str(row.get('Título de publicación', '')) if pd.notna(row.get('Título de publicación', '')) else ''
                    
                    cantidad = row.get('Cantidad', 1) if pd.notna(row.get('Cantidad', 1)) else 1
                    
                    # Limpiar el título para mejor coincidencia
                    titulo_limpio = titulo.strip() if titulo else ''
                    
                    # Obtener tasa de cambio actual del session state
                    tasa_actual = st.session_state.get('tasa_cambio_actual', 1350.0)
                    
                    if titulo_limpio in costos_producto:
                        # Obtener costo en USD y convertir a ARS
                        costo_usd = costos_producto[titulo_limpio]
                        return costo_usd * cantidad * tasa_actual
                    
                    # Si no encuentra coincidencia exacta, buscar coincidencia parcial
                    for titulo_costo in costos_producto.keys():
                        if titulo_limpio.lower() in titulo_costo.lower() or titulo_costo.lower() in titulo_limpio.lower():
                            costo_usd = costos_producto[titulo_costo]
                            return costo_usd * cantidad * tasa_actual
                    
                    return 0.0
                
                resultado_final['Costo por producto'] = resultado_final.apply(calcular_costo_producto, axis=1)
            else:
                st.info("ℹ️ No se cargaron costos por producto. Solo se consideran costos de operación.")
                resultado_final['Costo por producto'] = 0.0
            
            # Calcular ganancia neta usando la fórmula específica del usuario
            # CORRECCIÓN: IVA se calcula sobre el neto de la venta (Total - Costos de operación)
            
            # Constantes de IVA
            IVA_RATE = 0.21  # 21% IVA
            
            # Calcular neto de la venta (Total de la venta - Costos de operación)
            resultado_final['Neto de la venta'] = resultado_final['Total de la venta'] - resultado_final['Costos de operación']
            
            # Calcular IVA sobre el neto de la venta
            resultado_final['IVA de la venta'] = resultado_final['Neto de la venta'] * IVA_RATE
            
            # Calcular valor sin IVA (neto de la venta - IVA)
            resultado_final['Neto sin IVA'] = resultado_final['Neto de la venta'] - resultado_final['IVA de la venta']
            
            # Costos de operación sin IVA (asumiendo que incluyen IVA)
            resultado_final['Costos de operación (sin IVA)'] = resultado_final['Costos de operación'] / (1 + IVA_RATE)
            
            # Costo por producto ya está sin IVA (se mantiene igual)
            resultado_final['Costo por producto (sin IVA)'] = resultado_final['Costo por producto']
            
            # Calcular ganancia neta real (sin IVA) - INCLUYENDO GASTOS DE TRABAJO
            # Los costos de operación ya están incluidos en el neto de la venta
            gastos_trabajo_total = st.session_state.get('gastos_trabajo', 0.0)
            gastos_por_venta = gastos_trabajo_total / len(resultado_final) if len(resultado_final) > 0 else 0
            
            resultado_final['Gastos de trabajo'] = gastos_por_venta
            resultado_final['Ganancia neta (sin IVA)'] = (
                resultado_final['Neto sin IVA'] -
                resultado_final['Costo por producto (sin IVA)'] -
                resultado_final['Gastos de trabajo']
            )
            
            # Calcular porcentaje de ganancia neta real (sin IVA)
            resultado_final['% Ganancia Neta (sin IVA)'] = np.where(
                resultado_final['Neto sin IVA'] > 0,
                (resultado_final['Ganancia neta (sin IVA)'] / resultado_final['Neto sin IVA']) * 100,
                0
            )
            
            # Reorganizar columnas según solicitud del usuario
            columnas_finales = [
                'Fecha de venta',
                'Título de publicación', 
                'Total de la venta',
                'Neto de la venta',
                'Costos de operación',
                'Costo por producto',
                'Gastos de trabajo',
                'Ganancia neta (sin IVA)',
                '% Ganancia Neta (sin IVA)'
            ]
            
            # Agregar información de tasa de cambio
            tasa_actual = st.session_state.get('tasa_cambio_actual', 1350.0)
            st.info(f"💱 **Tasa de cambio:** ${tasa_actual:.2f} ARS/USD - Los costos en USD se ajustan automáticamente")
            
            # Filtrar solo las columnas que existen
            columnas_existentes = [col for col in columnas_finales if col in resultado_final.columns]
            resultado_final_ordenado = resultado_final[columnas_existentes]
            

            
            # Contenedor para la tabla con mejor estilo
            st.markdown("""
            <div class="table-container">
            """, unsafe_allow_html=True)
            st.dataframe(resultado_final_ordenado, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Mostrar resumen de ganancias
            total_ventas = resultado_final['Total de la venta'].sum()
            total_neto_venta = resultado_final['Neto de la venta'].sum()
            total_iva_venta = resultado_final['IVA de la venta'].sum()
            total_costos_operacion = resultado_final['Costos de operación'].sum()
            total_costos_producto = resultado_final['Costo por producto'].sum()
            ganancia_total = resultado_final['Ganancia neta (sin IVA)'].sum()
            
            # Calcular porcentaje de ganancia neta promedio
            porcentaje_ganancia_promedio = resultado_final['% Ganancia Neta (sin IVA)'].mean()
            
            # Calcular margen sobre costo (Ganancia / Costos de producto * 100)
            # Incluir gastos de trabajo en el denominador
            costos_totales_incluyendo_gastos = total_costos_producto + st.session_state.get('gastos_trabajo', 0.0)
            margen_sobre_costo = (ganancia_total / costos_totales_incluyendo_gastos * 100) if costos_totales_incluyendo_gastos > 0 else 0
            
            # Inicializar gastos de trabajo en session state
            if 'gastos_trabajo' not in st.session_state:
                st.session_state['gastos_trabajo'] = 0.0
            
            # Cargar gastos persistentes si existen
            gastos_file = "gastos_trabajo.json"
            if os.path.exists(gastos_file):
                try:
                    with open(gastos_file, 'r') as f:
                        gastos_data = json.load(f)
                        st.session_state['lista_gastos'] = gastos_data.get('lista_gastos', [])
                        st.session_state['gastos_trabajo'] = gastos_data.get('total', 0.0)
                except:
                    st.session_state['lista_gastos'] = []
                    st.session_state['gastos_trabajo'] = 0.0
            else:
                st.session_state['lista_gastos'] = []
            
            # KPIs principales
            st.markdown("""
            <div class="kpi-header">
                <h3>📊 KPIs - Análisis de Ganancias</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Primera fila - 4 KPIs principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">Total Ventas</div>
                    <div class="result-value">${total_ventas:,.0f}</div>
                    <div class="result-label">ARS</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">Neto de la Venta</div>
                    <div class="result-value">${total_neto_venta:,.0f}</div>
                    <div class="result-label">ARS</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">IVA de la Venta</div>
                    <div class="result-value">${total_iva_venta:,.0f}</div>
                    <div class="result-label">ARS</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">Costos de Operación</div>
                    <div class="result-value">${total_costos_operacion:,.0f}</div>
                    <div class="result-label">ARS</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Segunda fila - 4 KPIs de rentabilidad
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">Gastos de Trabajo</div>
                    <div class="result-value">${st.session_state['gastos_trabajo']:,.0f}</div>
                    <div class="result-label">ARS</div>
                </div>
                """, unsafe_allow_html=True)
            with col6:
                if ganancia_total >= 0:
                    st.markdown(f"""
                    <div class="result-card" style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border: 2px solid #28a745;">
                        <div class="result-label" style="color: #155724;">Ganancia Neta (sin IVA)</div>
                        <div class="result-value" style="color: #155724;">${ganancia_total:,.0f}</div>
                        <div class="result-label" style="color: #155724;">ARS</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card" style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border: 2px solid #dc3545;">
                        <div class="result-label" style="color: #721c24;">Ganancia Neta (sin IVA)</div>
                        <div class="result-value" style="color: #721c24;">${ganancia_total:,.0f}</div>
                        <div class="result-label" style="color: #721c24;">ARS</div>
                    </div>
                    """, unsafe_allow_html=True)
            with col7:
                if porcentaje_ganancia_promedio >= 0:
                    st.markdown(f"""
                    <div class="result-card" style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border: 2px solid #28a745;">
                        <div class="result-label" style="color: #155724;">% Margen Neto</div>
                        <div class="result-value" style="color: #155724;">{porcentaje_ganancia_promedio:.0f}%</div>
                        <div class="result-label" style="color: #155724;">Promedio</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card" style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border: 2px solid #dc3545;">
                        <div class="result-label" style="color: #721c24;">% Margen Neto</div>
                        <div class="result-value" style="color: #721c24;">{porcentaje_ganancia_promedio:.0f}%</div>
                        <div class="result-label" style="color: #721c24;">Promedio</div>
                    </div>
                    """, unsafe_allow_html=True)
            with col8:
                if margen_sobre_costo >= 0:
                    st.markdown(f"""
                    <div class="result-card" style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border: 2px solid #28a745;">
                        <div class="result-label" style="color: #155724;">% Margen S/Costo</div>
                        <div class="result-value" style="color: #155724;">{margen_sobre_costo:.0f}%</div>
                        <div class="result-label" style="color: #155724;">Sobre Costos</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card" style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border: 2px solid #dc3545;">
                        <div class="result-label" style="color: #721c24;">% Margen S/Costo</div>
                        <div class="result-value" style="color: #721c24;">{margen_sobre_costo:.0f}%</div>
                        <div class="result-label" style="color: #721c24;">Sobre Costos</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Sección de Gastos de Trabajo
            st.markdown("---")
            st.markdown("### 💼 Gestión de Gastos de Trabajo")
            
            # Formulario para agregar gastos
            with st.form("gastos_trabajo_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    descripcion = st.text_input("Descripción del gasto", key="descripcion_gasto")
                with col2:
                    monto = st.number_input("Monto (ARS)", min_value=0.0, value=0.0, step=100.0, key="monto_gasto")
                with col3:
                    fecha = st.date_input("Fecha", value=datetime.now().date(), key="fecha_gasto")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("➕ Agregar Gasto", use_container_width=True):
                        if descripcion and monto > 0:
                            # Agregar gasto a la lista
                            if 'lista_gastos' not in st.session_state:
                                st.session_state['lista_gastos'] = []
                            
                            nuevo_gasto = {
                                'descripcion': descripcion,
                                'monto': monto,
                                'fecha': fecha.strftime('%Y-%m-%d')
                            }
                            st.session_state['lista_gastos'].append(nuevo_gasto)
                            
                            # Actualizar total de gastos
                            st.session_state['gastos_trabajo'] = sum(gasto['monto'] for gasto in st.session_state['lista_gastos'])
                            save_gastos_trabajo()  # Guardar gastos persistentemente
                            st.success(f"✅ Gasto agregado: {descripcion} - ${monto:,.0f}")
                            st.rerun()
                        else:
                            st.error("❌ Por favor completa la descripción y el monto")
                
                with col2:
                    if st.form_submit_button("🗑️ Limpiar Todos", use_container_width=True):
                        st.session_state['lista_gastos'] = []
                        st.session_state['gastos_trabajo'] = 0.0
                        save_gastos_trabajo()  # Guardar gastos persistentemente
                        st.success("✅ Todos los gastos han sido eliminados")
                        st.rerun()
            
            # Mostrar lista de gastos
            if 'lista_gastos' in st.session_state and st.session_state['lista_gastos']:
                st.markdown("#### 📋 Gastos Registrados")
                
                # Mostrar tabla con botones de eliminar
                for i, gasto in enumerate(st.session_state['lista_gastos']):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"**{gasto['descripcion']}**")
                    with col2:
                        st.write(f"${gasto['monto']:,.0f}")
                    with col3:
                        st.write(gasto['fecha'])
                    with col4:
                        if st.button("🗑️", key=f"eliminar_gasto_{i}"):
                            st.session_state['lista_gastos'].pop(i)
                            st.session_state['gastos_trabajo'] = sum(gasto['monto'] for gasto in st.session_state['lista_gastos'])
                            save_gastos_trabajo()  # Guardar gastos persistentemente
                            st.success("✅ Gasto eliminado")
                            st.rerun()
                
                # Mostrar total
                st.markdown(f"**💰 Total Gastos de Trabajo: ${st.session_state['gastos_trabajo']:,.0f}**")