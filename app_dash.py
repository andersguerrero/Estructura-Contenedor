import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import warnings
import io
import base64
import json
from dash.exceptions import PreventUpdate

warnings.filterwarnings('ignore')

# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Sistema de Análisis de Costos y Ganancias"

# Configuración de la página
app.config.suppress_callback_exceptions = True

# Constantes
CONTAINER_40HQ_CBM = 70.0

# Variables globales para almacenar datos
global_data = {
    'productos': [],
    'precio_dolar': 1000.0,
    'ddi_pct': 18.0,
    'tasas_pct': 3.0,
    'iva_pct': 21.0,
    'iva_adic_pct': 20.0,
    'ganancias_pct': 6.0,
    'iibb_pct': 2.0,
    'seguro_pct': 0.5,
    'agente_pct': 4.0,
    'despachante_pct': 1.0,
    'tipo_cambio_inventario': 1300.0
}

# Cargar productos desde CSV si existe
if os.path.exists('productos_guardados.csv'):
    try:
        df_csv = pd.read_csv('productos_guardados.csv')
        if not df_csv.empty:
            global_data['productos'] = df_csv.to_dict('records')
    except Exception as e:
        global_data['productos'] = []

# Layout principal
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("📊 Sistema de Análisis de Costos y Ganancias", 
                   className="text-center mb-4 text-primary"),
            html.Hr()
        ])
    ]),
    
    # Navegación
            dbc.Row([
            dbc.Col([
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("🏠 Inicio", id="nav-inicio", n_clicks=0)),
                    dbc.NavItem(dbc.NavLink("🚢 Contenedor", id="nav-contenedor", n_clicks=0)),
                    dbc.NavItem(dbc.NavLink("💰 Ganancias", id="nav-ganancias", n_clicks=0)),
                    dbc.NavItem(dbc.NavLink("📦 Inventario", id="nav-inventario", n_clicks=0)),
                ], pills=True, className="mb-4")
            ])
        ]),
    
    # Contenido principal
    html.Div(id="page-content"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Sistema de Análisis de Costos y Ganancias - Desarrollado con Dash", 
                   className="text-center text-muted")
        ])
    ])
], fluid=True)

# Callback para navegación
@app.callback(
    Output("page-content", "children"),
    [Input("nav-inicio", "n_clicks"),
     Input("nav-contenedor", "n_clicks"),
     Input("nav-ganancias", "n_clicks"),
     Input("nav-inventario", "n_clicks"),
     Input("btn-contenedor", "n_clicks"),
     Input("btn-ganancias", "n_clicks"),
     Input("btn-inventario", "n_clicks"),
     Input("btn-dashboard", "n_clicks")]
)
def display_page(inicio_clicks, contenedor_clicks, ganancias_clicks, inventario_clicks,
                btn_contenedor, btn_ganancias, btn_inventario, btn_dashboard):
    ctx = callback_context
    if not ctx.triggered:
        return create_home_page()
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id in ["nav-inicio", "btn-inicio"]:
        return create_home_page()
    elif button_id in ["nav-contenedor", "btn-contenedor"]:
        return create_contenedor_page()
    elif button_id in ["nav-ganancias", "btn-ganancias"]:
        return create_ganancias_page()
    elif button_id in ["nav-inventario", "btn-inventario"]:
        return create_inventario_page()
    elif button_id == "btn-dashboard":
        return create_home_page()  # Dashboard por ahora es la página de inicio
    
    return create_home_page()

def create_home_page():
    """Página de inicio"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🏠 Bienvenido al Sistema de Análisis", className="text-center mb-4"),
                html.P("Este sistema te permite analizar costos, gestionar contenedores y calcular ganancias.", 
                       className="text-center mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🚢 Módulo Contenedor", className="card-title"),
                        html.P("Gestiona productos y calcula costos de importación."),
                        dbc.Button("Ir al Contenedor", id="btn-contenedor", color="primary")
                    ])
                ], className="mb-3")
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("💰 Módulo Ganancias", className="card-title"),
                        html.P("Analiza reportes de MercadoLibre y calcula ganancias."),
                        dbc.Button("Ir a Ganancias", id="btn-ganancias", color="success")
                    ])
                ], className="mb-3")
            ], width=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📦 Módulo Inventario", className="card-title"),
                        html.P("Gestiona stock y calcula valor del inventario."),
                        dbc.Button("Ir al Inventario", id="btn-inventario", color="info")
                    ])
                ], className="mb-3")
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📊 Dashboard", className="card-title"),
                        html.P("Vista general de todos los módulos."),
                        dbc.Button("Ver Dashboard", id="btn-dashboard", color="warning")
                    ])
                ], className="mb-3")
            ], width=6)
        ])
    ])

def create_contenedor_page():
    """Página del módulo contenedor"""
    try:
        from modules.contenedor_dash import create_contenedor_module
        return create_contenedor_module()
    except Exception as e:
        return dbc.Container([
            html.H2("🚢 Módulo Contenedor", className="mb-4"),
            dbc.Alert(f"Error cargando módulo: {str(e)}", color="danger"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("⚙️ Configuración"),
                        dbc.CardBody([
                            html.Label("💱 Precio del Dólar (ARS)"),
                            dcc.Input(
                                id="precio-dolar",
                                type="number",
                                value=1000.0,
                                step=1.0,
                                className="form-control mb-3"
                            ),
                            dbc.Button("💾 Guardar", id="save-config", color="primary", className="w-100")
                        ])
                    ], className="mb-4")
                ], width=3),
                dbc.Col([
                    html.Div(id="contenedor-content")
                ], width=9)
            ])
        ])

def create_ganancias_page():
    """Página del módulo ganancias"""
    from modules.ganancias_dash import create_ganancias_module
    return create_ganancias_module()

def create_inventario_page():
    """Página del módulo inventario"""
    from modules.inventario_dash import create_inventario_module
    return create_inventario_module()

# Callbacks para el módulo de contenedor
@app.callback(
    Output("contenedor-content", "children"),
    [Input("save-config", "n_clicks"),
     Input("add-producto", "n_clicks")],
    [State("precio-dolar", "value"),
     State("ddi-pct", "value"),
     State("tasas-pct", "value"),
     State("iva-pct", "value"),
     State("iva-adic-pct", "value"),
     State("ganancias-pct", "value"),
     State("iibb-pct", "value"),
     State("seguro-pct", "value"),
     State("agente-pct", "value"),
     State("despachante-pct", "value"),
     State("nombre-producto", "value"),
     State("precio-fob", "value"),
     State("cantidad-total", "value"),
     State("piezas-caja", "value"),
     State("peso-caja", "value"),
     State("largo", "value"),
     State("ancho", "value"),
     State("alto", "value")]
)
def update_contenedor_config(save_clicks, add_clicks, precio_dolar, ddi_pct, tasas_pct, iva_pct, 
                           iva_adic_pct, ganancias_pct, iibb_pct, seguro_pct, agente_pct, despachante_pct,
                           nombre, precio_fob, cantidad, piezas_caja, peso_caja, largo, ancho, alto):
    
    ctx = callback_context
    if not ctx.triggered:
        return html.Div([
            html.H4("📊 Análisis de Contenedor"),
            html.P("Configura los parámetros y agrega productos para comenzar el análisis.")
        ])
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "save-config":
        # Guardar configuración
        global_data['precio_dolar'] = precio_dolar or 1000.0
        global_data['ddi_pct'] = ddi_pct or 18.0
        global_data['tasas_pct'] = tasas_pct or 3.0
        global_data['iva_pct'] = iva_pct or 21.0
        global_data['iva_adic_pct'] = iva_adic_pct or 20.0
        global_data['ganancias_pct'] = ganancias_pct or 6.0
        global_data['iibb_pct'] = iibb_pct or 2.0
        global_data['seguro_pct'] = seguro_pct or 0.5
        global_data['agente_pct'] = agente_pct or 4.0
        global_data['despachante_pct'] = despachante_pct or 1.0
        
        return dbc.Alert("✅ Configuración guardada exitosamente!", color="success")
    
    elif button_id == "add-producto":
        # Agregar producto
        if all([nombre, precio_fob, cantidad, piezas_caja, peso_caja, largo, ancho, alto]):
            # Calcular CBM
            cbm_caja = (largo * ancho * alto) / 1000000  # Convertir a m³
            cbm_total = cbm_caja * (cantidad / piezas_caja)
            peso_total = peso_caja * (cantidad / piezas_caja)
            
            # Crear producto
            producto = {
                'Nombre': nombre,
                'Precio FOB (USD)': precio_fob,
                'Cantidad Total': cantidad,
                'Piezas por Caja': piezas_caja,
                'Peso por Caja (kg)': peso_caja,
                'Largo (cm)': largo,
                'Ancho (cm)': ancho,
                'Alto (cm)': alto,
                'CBM por Caja': cbm_caja,
                'CBM Total': cbm_total,
                'Peso Total (kg)': peso_total,
                'Flete por Producto (USD)': 0,  # Se calculará después
                'Gastos Fijos por Producto (USD)': 0  # Se calculará después
            }
            
            global_data['productos'].append(producto)
            
            # Guardar en CSV
            df = pd.DataFrame(global_data['productos'])
            df.to_csv('productos_guardados.csv', index=False)
            
            return dbc.Alert(f"✅ Producto '{nombre}' agregado exitosamente!", color="success")
        else:
            return dbc.Alert("❌ Por favor completa todos los campos del producto", color="danger")
    
    return html.Div([
        html.H4("📊 Análisis de Contenedor"),
        html.P("Configura los parámetros y agrega productos para comenzar el análisis."),
        
        # Mostrar productos si existen
        html.Div(id="productos-display")
    ])

@app.callback(
    Output("inventario-content", "children"),
    [Input("analyze-inventario", "n_clicks")],
    [State("tipo-cambio-inventario", "value")]
)
def update_inventario_analysis(n_clicks, tipo_cambio):
    if n_clicks and tipo_cambio:
        global_data['tipo_cambio_inventario'] = tipo_cambio
        return dbc.Alert(f"✅ Tipo de cambio actualizado a {tipo_cambio} ARS/USD", color="success")
    
    return html.Div([
        html.H4("📦 Análisis de Inventario"),
        html.P("Configura el tipo de cambio y carga un archivo Excel con tu inventario.")
    ])

# Callbacks para el módulo de ganancias
@app.callback(
    Output('ganancias-content', 'children'),
    [Input('analyze-ganancias', 'n_clicks')],
    [State('upload-mercadolibre', 'contents'),
     State('upload-mercadolibre', 'filename'),
     State('upload-costos', 'contents'),
     State('upload-costos', 'filename')]
)
def process_ganancias_analysis(n_clicks, mercadolibre_contents, mercadolibre_filename, 
                             costos_contents, costos_filename):
    if not n_clicks:
        return html.Div([
            html.H4("💰 Análisis de Ganancias"),
            html.P("Carga los reportes de MercadoLibre y costos para comenzar el análisis.")
        ])
    
    from modules.ganancias_dash import procesar_reporte_mercadolibre, procesar_costos, calcular_ganancias, create_ganancias_table, create_ganancias_summary, create_ganancias_chart
    
    # Procesar reporte de MercadoLibre
    df_ventas, info_ventas = procesar_reporte_mercadolibre(mercadolibre_contents, mercadolibre_filename)
    if df_ventas is None:
        return dbc.Alert(f"❌ Error en reporte de MercadoLibre: {info_ventas}", color="danger")
    
    # Procesar archivo de costos
    df_costos, info_costos = procesar_costos(costos_contents, costos_filename)
    if df_costos is None:
        return dbc.Alert(f"❌ Error en archivo de costos: {info_costos}", color="danger")
    
    # Calcular ganancias
    df_resultado, metricas = calcular_ganancias(df_ventas, df_costos)
    if df_resultado is None:
        return dbc.Alert(f"❌ Error calculando ganancias: {metricas}", color="danger")
    
    return html.Div([
        html.H4("📊 Resumen de Ganancias", className="mb-3"),
        create_ganancias_summary(metricas),
        html.Hr(),
        html.H4("📈 Gráfico de Ganancias", className="mb-3"),
        create_ganancias_chart(df_resultado),
        html.Hr(),
        html.H4("📋 Detalle de Ventas", className="mb-3"),
        create_ganancias_table(df_resultado)
    ])

# Callback unificado para inventario
@app.callback(
    Output('inventario-content', 'children'),
    [Input('analyze-inventario', 'n_clicks'),
     Input('tipo-cambio-inventario', 'value')],
    [State('upload-inventario', 'contents'),
     State('upload-inventario', 'filename'),
     State('upload-costos-inventario', 'contents'),
     State('upload-costos-inventario', 'filename')]
)
def process_inventario_analysis(n_clicks, tipo_cambio, inventario_contents, inventario_filename,
                              costos_contents, costos_filename):
    ctx = callback_context
    if not ctx.triggered:
        return html.Div([
            html.H4("📦 Análisis de Inventario"),
            html.P("Configura el tipo de cambio y carga los archivos para comenzar el análisis.")
        ])
    
    # Si solo cambió el tipo de cambio, no procesar
    if ctx.triggered[0]['prop_id'] == 'tipo-cambio-inventario.value':
        return html.Div([
            html.H4("📦 Análisis de Inventario"),
            html.P("Configura el tipo de cambio y carga los archivos para comenzar el análisis.")
        ])
    
    if not n_clicks:
        return html.Div([
            html.H4("📦 Análisis de Inventario"),
            html.P("Configura el tipo de cambio y carga los archivos para comenzar el análisis.")
        ])
    
    if not tipo_cambio:
        return dbc.Alert("❌ Por favor ingresa el tipo de cambio", color="danger")
    
    from modules.inventario_dash import procesar_inventario, procesar_costos_inventario, calcular_valuacion_inventario, create_inventario_table, create_inventario_summary, create_inventario_chart
    
    # Procesar inventario
    df_inventario, info_inventario = procesar_inventario(inventario_contents, inventario_filename)
    if df_inventario is None:
        return dbc.Alert(f"❌ Error en archivo de inventario: {info_inventario}", color="danger")
    
    # Procesar costos
    df_costos, info_costos = procesar_costos_inventario(costos_contents, costos_filename)
    if df_costos is None:
        return dbc.Alert(f"❌ Error en archivo de costos: {info_costos}", color="danger")
    
    # Calcular valuación
    df_resultado, metricas = calcular_valuacion_inventario(df_inventario, df_costos, tipo_cambio)
    if df_resultado is None:
        return dbc.Alert(f"❌ Error calculando valuación: {metricas}", color="danger")
    
    return html.Div([
        html.H4("📊 Resumen del Inventario", className="mb-3"),
        create_inventario_summary(metricas),
        html.Hr(),
        html.H4("📈 Gráfico de Ganancia Potencial", className="mb-3"),
        create_inventario_chart(df_resultado),
        html.Hr(),
        html.H4("📋 Detalle del Inventario", className="mb-3"),
        create_inventario_table(df_resultado)
    ])

# Callback para mostrar productos y cálculos
@app.callback(
    Output("productos-display", "children"),
    [Input("save-config", "n_clicks"),
     Input("add-producto", "n_clicks")]
)
def display_productos(save_clicks, add_clicks):
    if not global_data['productos']:
        return html.Div("No hay productos agregados aún.")
    
    from modules.contenedor_dash import calcular_dataframe_productos, create_product_table, create_summary_cards
    
    # Calcular DataFrame con todos los cálculos
    df_productos = calcular_dataframe_productos(
        global_data['productos'],
        global_data['precio_dolar'],
        global_data['ddi_pct'],
        global_data['tasas_pct'],
        global_data['iva_pct'],
        global_data['iva_adic_pct'],
        global_data['ganancias_pct'],
        global_data['iibb_pct'],
        global_data['seguro_pct'],
        global_data['agente_pct'],
        global_data['despachante_pct']
    )
    
    if df_productos.empty:
        return html.Div("Error en los cálculos.")
    
    return html.Div([
        html.H4("📊 Resumen del Contenedor", className="mb-3"),
        create_summary_cards(df_productos, global_data['precio_dolar']),
        html.Hr(),
        html.H4("📋 Tabla de Productos", className="mb-3"),
        create_product_table(df_productos)
    ])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050) 