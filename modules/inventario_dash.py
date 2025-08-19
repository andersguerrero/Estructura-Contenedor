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

warnings.filterwarnings('ignore')

def create_inventario_module():
    """Crear el módulo completo de inventario para Dash"""
    
    layout = dbc.Container([
        html.H2("📦 Módulo Gestión de Inventario", className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("⚙️ Configuración"),
                    dbc.CardBody([
                        html.Label("💱 Tipo de Cambio (ARS/USD)"),
                        dcc.Input(
                            id="tipo-cambio-inventario",
                            type="number",
                            value=1300.0,
                            step=1.0,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("📤 Cargar Inventario (Excel)"),
                        dcc.Upload(
                            id='upload-inventario',
                            children=html.Div([
                                'Arrastra y suelta o ',
                                html.A('selecciona un archivo Excel')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=False
                        ),
                        
                        html.Hr(),
                        
                        html.Label("📋 Cargar Costos (Excel)"),
                        dcc.Upload(
                            id='upload-costos-inventario',
                            children=html.Div([
                                'Arrastra y suelta o ',
                                html.A('selecciona un archivo Excel')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=False
                        ),
                        
                        dbc.Button("📊 Analizar Inventario", id="analyze-inventario", color="primary", className="w-100 mt-3")
                    ])
                ], className="mb-4")
            ], width=3),
            
            dbc.Col([
                html.Div(id="inventario-content")
            ], width=9)
        ])
    ])
    
    return layout

def procesar_inventario(contents, filename):
    """Procesar archivo de inventario"""
    if contents is None:
        return None, "No se cargó ningún archivo"
    
    try:
        # Decodificar el archivo
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Leer el archivo Excel
        df = pd.read_excel(io.BytesIO(decoded))
        
        # Verificar columnas requeridas
        required_columns = ['nombre', 'cantidad']
        if not all(col in df.columns for col in required_columns):
            return None, f"El archivo debe contener las columnas: {required_columns}"
        
        # Limpiar datos
        df = df.dropna(subset=['nombre'])
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
        
        return df, {
            'total_productos': len(df),
            'total_unidades': df['cantidad'].sum(),
            'filename': filename
        }
        
    except Exception as e:
        return None, f"Error procesando archivo: {str(e)}"

def procesar_costos_inventario(contents, filename):
    """Procesar archivo de costos para inventario"""
    if contents is None:
        return None, "No se cargó ningún archivo"
    
    try:
        # Decodificar el archivo
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Leer el archivo Excel
        df = pd.read_excel(io.BytesIO(decoded))
        
        # Verificar columnas
        if 'nombre' in df.columns and 'costo_unitario_usd' in df.columns:
            df_costos = df[['nombre', 'costo_unitario_usd']].copy()
            df_costos = df_costos.dropna()
            return df_costos, {
                'total_productos': len(df_costos),
                'filename': filename
            }
        else:
            return None, "El archivo debe contener columnas 'nombre' y 'costo_unitario_usd'"
        
    except Exception as e:
        return None, f"Error procesando archivo: {str(e)}"

def calcular_valuacion_inventario(df_inventario, df_costos, tipo_cambio):
    """Calcular valuación del inventario"""
    if df_inventario is None or df_costos is None:
        return None, None
    
    try:
        # Crear diccionario de costos
        costos_dict = dict(zip(df_costos['nombre'], df_costos['costo_unitario_usd']))
        
        # Agregar costos al inventario
        df_inventario['costo_unitario_usd'] = df_inventario['nombre'].map(costos_dict)
        df_inventario['costo_unitario_usd'] = df_inventario['costo_unitario_usd'].fillna(0)
        
        # Calcular valores en USD
        df_inventario['costo_total_usd'] = df_inventario['costo_unitario_usd'] * df_inventario['cantidad']
        
        # Calcular valores en ARS
        df_inventario['costo_unitario_ars'] = df_inventario['costo_unitario_usd'] * tipo_cambio
        df_inventario['costo_total_ars'] = df_inventario['costo_total_usd'] * tipo_cambio
        
        # Calcular precios de venta (ejemplo: 30% de ganancia)
        df_inventario['precio_venta_ars'] = df_inventario['costo_unitario_ars'] * 1.3
        df_inventario['valor_venta_total_ars'] = df_inventario['precio_venta_ars'] * df_inventario['cantidad']
        
        # Calcular ganancias potenciales
        df_inventario['ganancia_potencial_ars'] = df_inventario['valor_venta_total_ars'] - df_inventario['costo_total_ars']
        df_inventario['margen_potencial'] = (df_inventario['ganancia_potencial_ars'] / df_inventario['costo_total_ars'] * 100).fillna(0)
        
        # Métricas agregadas
        total_costo_usd = df_inventario['costo_total_usd'].sum()
        total_costo_ars = df_inventario['costo_total_ars'].sum()
        total_valor_venta = df_inventario['valor_venta_total_ars'].sum()
        total_ganancia_potencial = df_inventario['ganancia_potencial_ars'].sum()
        total_unidades = df_inventario['cantidad'].sum()
        
        metricas = {
            'total_costo_usd': total_costo_usd,
            'total_costo_ars': total_costo_ars,
            'total_valor_venta': total_valor_venta,
            'total_ganancia_potencial': total_ganancia_potencial,
            'total_unidades': total_unidades,
            'margen_promedio': (total_ganancia_potencial / total_costo_ars * 100) if total_costo_ars > 0 else 0
        }
        
        return df_inventario, metricas
        
    except Exception as e:
        return None, f"Error calculando valuación: {str(e)}"

def create_inventario_table(df_inventario):
    """Crear tabla de inventario con Dash DataTable"""
    if df_inventario is None or df_inventario.empty:
        return html.Div("No hay datos para mostrar")
    
    # Preparar datos para la tabla
    columns = [
        {"name": "Producto", "id": "nombre"},
        {"name": "Cantidad", "id": "cantidad"},
        {"name": "Costo Unitario USD", "id": "costo_unitario_usd"},
        {"name": "Costo Total USD", "id": "costo_total_usd"},
        {"name": "Costo Unitario ARS", "id": "costo_unitario_ars"},
        {"name": "Costo Total ARS", "id": "costo_total_ars"},
        {"name": "Precio Venta ARS", "id": "precio_venta_ars"},
        {"name": "Valor Venta Total ARS", "id": "valor_venta_total_ars"},
        {"name": "Ganancia Potencial ARS", "id": "ganancia_potencial_ars"},
        {"name": "Margen %", "id": "margen_potencial"}
    ]
    
    # Formatear datos
    data = []
    for _, row in df_inventario.iterrows():
        data.append({
            "nombre": row.get('nombre', ''),
            "cantidad": f"{row.get('cantidad', 0):,.0f}",
            "costo_unitario_usd": f"${row.get('costo_unitario_usd', 0):,.2f}",
            "costo_total_usd": f"${row.get('costo_total_usd', 0):,.2f}",
            "costo_unitario_ars": f"${row.get('costo_unitario_ars', 0):,.0f}",
            "costo_total_ars": f"${row.get('costo_total_ars', 0):,.0f}",
            "precio_venta_ars": f"${row.get('precio_venta_ars', 0):,.0f}",
            "valor_venta_total_ars": f"${row.get('valor_venta_total_ars', 0):,.0f}",
            "ganancia_potencial_ars": f"${row.get('ganancia_potencial_ars', 0):,.0f}",
            "margen_potencial": f"{row.get('margen_potencial', 0):.1f}%"
        })
    
    return dash.dash_table.DataTable(
        id='inventario-table',
        columns=columns,
        data=data,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
            {'if': {'column_id': 'ganancia_potencial_ars'}, 'color': 'green'},
            {'if': {'column_id': 'margen_potencial'}, 'color': 'blue'}
        ],
        page_size=10
    )

def create_inventario_summary(metricas):
    """Crear tarjetas de resumen de inventario"""
    if not metricas:
        return html.Div("No hay métricas para mostrar")
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{metricas['total_unidades']:,.0f}", className="card-title text-center"),
                    html.P("Total Unidades", className="card-text text-center")
                ])
            ], color="info", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${metricas['total_costo_ars']:,.0f}", className="card-title text-center"),
                    html.P("Valor Inventario ARS", className="card-text text-center")
                ])
            ], color="warning", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${metricas['total_valor_venta']:,.0f}", className="card-title text-center"),
                    html.P("Valor Venta Potencial ARS", className="card-text text-center")
                ])
            ], color="success", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${metricas['total_ganancia_potencial']:,.0f}", className="card-title text-center"),
                    html.P("Ganancia Potencial ARS", className="card-text text-center")
                ])
            ], color="primary", outline=True)
        ], width=3)
    ])

def create_inventario_chart(df_inventario):
    """Crear gráfico de inventario"""
    if df_inventario is None or df_inventario.empty:
        return html.Div("No hay datos para graficar")
    
    # Agrupar por producto
    df_agrupado = df_inventario.groupby('nombre').agg({
        'cantidad': 'sum',
        'costo_total_ars': 'sum',
        'valor_venta_total_ars': 'sum',
        'ganancia_potencial_ars': 'sum'
    }).reset_index()
    
    # Crear gráfico de barras
    fig = px.bar(
        df_agrupado.head(10),  # Top 10 productos
        x='nombre',
        y='ganancia_potencial_ars',
        title='Ganancia Potencial por Producto (Top 10)',
        labels={'ganancia_potencial_ars': 'Ganancia Potencial (ARS)', 'nombre': 'Producto'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    
    return dcc.Graph(figure=fig) 