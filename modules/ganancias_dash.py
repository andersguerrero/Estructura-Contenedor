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

def create_ganancias_module():
    """Crear el módulo completo de ganancias para Dash"""
    
    layout = dbc.Container([
        html.H2("💰 Módulo Análisis de Ganancias", className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📤 Cargar Reportes"),
                    dbc.CardBody([
                        html.Label("📊 Reporte de MercadoLibre (Excel)"),
                        dcc.Upload(
                            id='upload-mercadolibre',
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
                        
                        html.Label("📋 Archivo de Costos (Excel)"),
                        dcc.Upload(
                            id='upload-costos',
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
                        
                        dbc.Button("📊 Analizar Ganancias", id="analyze-ganancias", color="primary", className="w-100 mt-3")
                    ])
                ], className="mb-4")
            ], width=4),
            
            dbc.Col([
                html.Div(id="ganancias-content")
            ], width=8)
        ])
    ])
    
    return layout

def procesar_reporte_mercadolibre(contents, filename):
    """Procesar reporte de MercadoLibre"""
    if contents is None:
        return None, "No se cargó ningún archivo"
    
    try:
        # Decodificar el archivo
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Leer el archivo Excel
        df = pd.read_excel(io.BytesIO(decoded))
        
        # Procesar columnas
        if 'Fecha de venta' in df.columns:
            df['Fecha de venta'] = pd.to_datetime(df['Fecha de venta'])
        
        # Limpiar datos
        df = df.dropna(subset=['Título del ítem'])
        
        # Calcular métricas básicas
        total_ventas = len(df)
        total_ingresos = df['Precio unitario'].sum() if 'Precio unitario' in df.columns else 0
        total_comisiones = df['Comisión de MercadoLibre'].sum() if 'Comisión de MercadoLibre' in df.columns else 0
        
        return df, {
            'total_ventas': total_ventas,
            'total_ingresos': total_ingresos,
            'total_comisiones': total_comisiones,
            'filename': filename
        }
        
    except Exception as e:
        return None, f"Error procesando archivo: {str(e)}"

def procesar_costos(contents, filename):
    """Procesar archivo de costos"""
    if contents is None:
        return None, "No se cargó ningún archivo"
    
    try:
        # Decodificar el archivo
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Leer el archivo Excel
        df = pd.read_excel(io.BytesIO(decoded))
        
        # Procesar costos
        if 'Producto' in df.columns and 'Costo Unitario' in df.columns:
            df_costos = df[['Producto', 'Costo Unitario']].copy()
            df_costos = df_costos.dropna()
            return df_costos, {
                'total_productos': len(df_costos),
                'filename': filename
            }
        else:
            return None, "El archivo debe contener columnas 'Producto' y 'Costo Unitario'"
        
    except Exception as e:
        return None, f"Error procesando archivo: {str(e)}"

def calcular_ganancias(df_ventas, df_costos):
    """Calcular ganancias combinando ventas y costos"""
    if df_ventas is None or df_costos is None:
        return None
    
    try:
        # Crear diccionario de costos
        costos_dict = dict(zip(df_costos['Producto'], df_costos['Costo Unitario']))
        
        # Agregar costos a las ventas
        df_ventas['Costo Unitario'] = df_ventas['Título del ítem'].map(costos_dict)
        df_ventas['Costo Total'] = df_ventas['Costo Unitario'] * df_ventas['Cantidad']
        
        # Calcular ganancias
        df_ventas['Ganancia Bruta'] = df_ventas['Precio unitario'] - df_ventas['Costo Total']
        df_ventas['Ganancia Neta'] = df_ventas['Ganancia Bruta'] - df_ventas['Comisión de MercadoLibre']
        
        # Métricas agregadas
        total_ingresos = df_ventas['Precio unitario'].sum()
        total_costos = df_ventas['Costo Total'].sum()
        total_comisiones = df_ventas['Comisión de MercadoLibre'].sum()
        total_ganancia_bruta = df_ventas['Ganancia Bruta'].sum()
        total_ganancia_neta = df_ventas['Ganancia Neta'].sum()
        
        return df_ventas, {
            'total_ingresos': total_ingresos,
            'total_costos': total_costos,
            'total_comisiones': total_comisiones,
            'total_ganancia_bruta': total_ganancia_bruta,
            'total_ganancia_neta': total_ganancia_neta,
            'margen_bruto': (total_ganancia_bruta / total_ingresos * 100) if total_ingresos > 0 else 0,
            'margen_neto': (total_ganancia_neta / total_ingresos * 100) if total_ingresos > 0 else 0
        }
        
    except Exception as e:
        return None, f"Error calculando ganancias: {str(e)}"

def create_ganancias_table(df_ventas):
    """Crear tabla de ganancias con Dash DataTable"""
    if df_ventas is None or df_ventas.empty:
        return html.Div("No hay datos para mostrar")
    
    # Preparar datos para la tabla
    columns = [
        {"name": "Producto", "id": "Título del ítem"},
        {"name": "Cantidad", "id": "Cantidad"},
        {"name": "Precio Unitario", "id": "Precio unitario"},
        {"name": "Ingresos", "id": "Precio unitario"},
        {"name": "Costo Unitario", "id": "Costo Unitario"},
        {"name": "Costo Total", "id": "Costo Total"},
        {"name": "Comisión", "id": "Comisión de MercadoLibre"},
        {"name": "Ganancia Bruta", "id": "Ganancia Bruta"},
        {"name": "Ganancia Neta", "id": "Ganancia Neta"}
    ]
    
    # Formatear datos
    data = []
    for _, row in df_ventas.iterrows():
        data.append({
            "Título del ítem": row.get('Título del ítem', ''),
            "Cantidad": f"{row.get('Cantidad', 0):,.0f}",
            "Precio unitario": f"${row.get('Precio unitario', 0):,.2f}",
            "Costo Unitario": f"${row.get('Costo Unitario', 0):,.2f}",
            "Costo Total": f"${row.get('Costo Total', 0):,.2f}",
            "Comisión de MercadoLibre": f"${row.get('Comisión de MercadoLibre', 0):,.2f}",
            "Ganancia Bruta": f"${row.get('Ganancia Bruta', 0):,.2f}",
            "Ganancia Neta": f"${row.get('Ganancia Neta', 0):,.2f}"
        })
    
    return dash.dash_table.DataTable(
        id='ganancias-table',
        columns=columns,
        data=data,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
            {'if': {'column_id': 'Ganancia Bruta'}, 'color': 'green'},
            {'if': {'column_id': 'Ganancia Neta'}, 'color': 'blue'}
        ],
        page_size=15
    )

def create_ganancias_summary(metricas):
    """Crear tarjetas de resumen de ganancias"""
    if not metricas:
        return html.Div("No hay métricas para mostrar")
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${metricas['total_ingresos']:,.0f}", className="card-title text-center"),
                    html.P("Ingresos Totales", className="card-text text-center")
                ])
            ], color="success", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${metricas['total_costos']:,.0f}", className="card-title text-center"),
                    html.P("Costos Totales", className="card-text text-center")
                ])
            ], color="danger", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${metricas['total_ganancia_neta']:,.0f}", className="card-title text-center"),
                    html.P("Ganancia Neta", className="card-text text-center")
                ])
            ], color="primary", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{metricas['margen_neto']:.1f}%", className="card-title text-center"),
                    html.P("Margen Neto", className="card-text text-center")
                ])
            ], color="info", outline=True)
        ], width=3)
    ])

def create_ganancias_chart(df_ventas):
    """Crear gráfico de ganancias"""
    if df_ventas is None or df_ventas.empty:
        return html.Div("No hay datos para graficar")
    
    # Agrupar por producto
    df_agrupado = df_ventas.groupby('Título del ítem').agg({
        'Precio unitario': 'sum',
        'Costo Total': 'sum',
        'Ganancia Neta': 'sum'
    }).reset_index()
    
    # Crear gráfico de barras
    fig = px.bar(
        df_agrupado.head(10),  # Top 10 productos
        x='Título del ítem',
        y='Ganancia Neta',
        title='Ganancia Neta por Producto (Top 10)',
        labels={'Ganancia Neta': 'Ganancia Neta ($)', 'Título del ítem': 'Producto'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    
    return dcc.Graph(figure=fig) 