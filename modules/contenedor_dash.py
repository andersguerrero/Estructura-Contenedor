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

# Constantes
CONTAINER_40HQ_CBM = 70.0

def create_contenedor_module():
    """Crear el módulo completo de contenedor para Dash"""
    
    return dbc.Container([
        html.H2("🚢 Módulo Contenedor Completo", className="mb-4"),
        
        # Sidebar para configuración
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("⚙️ Configuración de Parámetros"),
                    dbc.CardBody([
                        html.Label("💱 Precio del Dólar (ARS)"),
                        dcc.Input(
                            id="precio-dolar",
                            type="number",
                            value=1000.0,
                            step=1.0,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("📊 DDI (%)"),
                        dcc.Input(
                            id="ddi-pct",
                            type="number",
                            value=18.0,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("📈 Tasas (%)"),
                        dcc.Input(
                            id="tasas-pct",
                            type="number",
                            value=3.0,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("🏛️ IVA (%)"),
                        dcc.Input(
                            id="iva-pct",
                            type="number",
                            value=21.0,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("🏛️ IVA Adicional (%)"),
                        dcc.Input(
                            id="iva-adic-pct",
                            type="number",
                            value=20.0,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("💰 Ganancias (%)"),
                        dcc.Input(
                            id="ganancias-pct",
                            type="number",
                            value=6.0,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("🏢 IIBB (%)"),
                        dcc.Input(
                            id="iibb-pct",
                            type="number",
                            value=2.0,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("🛡️ Seguro (%)"),
                        dcc.Input(
                            id="seguro-pct",
                            type="number",
                            value=0.5,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("👨‍💼 Agente (%)"),
                        dcc.Input(
                            id="agente-pct",
                            type="number",
                            value=4.0,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("📋 Despachante (%)"),
                        dcc.Input(
                            id="despachante-pct",
                            type="number",
                            value=1.0,
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        dbc.Button("💾 Guardar Configuración", id="save-config", color="primary", className="w-100 mb-3"),
                        
                        html.Hr(),
                        
                        html.H5("📦 Agregar Producto"),
                        html.Label("Nombre del Producto"),
                        dcc.Input(
                            id="nombre-producto",
                            type="text",
                            placeholder="Ej: Producto A",
                            className="form-control mb-3"
                        ),
                        
                        html.Label("Precio FOB (USD)"),
                        dcc.Input(
                            id="precio-fob",
                            type="number",
                            step=0.01,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("Cantidad Total"),
                        dcc.Input(
                            id="cantidad-total",
                            type="number",
                            step=1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("Piezas por Caja"),
                        dcc.Input(
                            id="piezas-caja",
                            type="number",
                            step=1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("Peso por Caja (kg)"),
                        dcc.Input(
                            id="peso-caja",
                            type="number",
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("Largo (cm)"),
                        dcc.Input(
                            id="largo",
                            type="number",
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("Ancho (cm)"),
                        dcc.Input(
                            id="ancho",
                            type="number",
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        html.Label("Alto (cm)"),
                        dcc.Input(
                            id="alto",
                            type="number",
                            step=0.1,
                            className="form-control mb-3"
                        ),
                        
                        dbc.Button("➕ Agregar Producto", id="add-producto", color="success", className="w-100")
                    ])
                ], className="mb-4")
            ], width=3),
            
            dbc.Col([
                html.Div(id="contenedor-content")
            ], width=9)
        ])
    ])

def calcular_dataframe_productos(productos, precio_dolar, ddi_pct, tasas_pct, iva_pct, iva_adic_pct, 
                               ganancias_pct, iibb_pct, seguro_pct, agente_pct, despachante_pct):
    """Calcula el DataFrame optimizado de productos con todos los cálculos necesarios"""
    if not productos:
        return pd.DataFrame()
    
    df = pd.DataFrame(productos)
    
    # Calcular totales
    total_cbm = df['CBM Total'].sum()
    total_peso = df['Peso Total (kg)'].sum()
    
    # Cálculos básicos
    df['FOB (USD)'] = df['Precio FOB (USD)'] * df['Cantidad Total']
    df['Seguro (USD)'] = df['FOB (USD)'] * (seguro_pct / 100)
    df['CIF (USD)'] = df['FOB (USD)'] + df['Seguro (USD)'] + df['Flete por Producto (USD)']
    
    # DDI
    df['DDI (USD)'] = df['CIF (USD)'] * (ddi_pct / 100)
    
    # Tasas
    df['Tasas (USD)'] = df['CIF (USD)'] * (tasas_pct / 100)
    
    # Antidumping
    if 'Antidumping (USD)' in df.columns:
        df['Antidumping (USD)'] = df['Antidumping (USD)'].fillna(0)
    else:
        df['Antidumping (USD)'] = 0
    
    # Valor IVA
    df['Valor IVA (USD)'] = df['CIF (USD)'] + df['DDI (USD)'] + df['Tasas (USD)']
    
    # Impuestos
    df['IVA (USD)'] = df['Valor IVA (USD)'] * (iva_pct / 100)
    df['IVA Adicional (USD)'] = df['Valor IVA (USD)'] * (iva_adic_pct / 100)
    df['Ganancias (USD)'] = df['Valor IVA (USD)'] * (ganancias_pct / 100)
    df['IIBB (USD)'] = df['Valor IVA (USD)'] * (iibb_pct / 100)
    
    # Otros gastos
    df['Agente (USD)'] = df['FOB (USD)'] * (agente_pct / 100)
    df['Despachante (USD)'] = df['FOB (USD)'] * (despachante_pct / 100)
    
    # Costos
    df['Costo Base (USD)'] = (df['CIF (USD)'] + df['DDI (USD)'] + df['Tasas (USD)'] + df['Antidumping (USD)'])
    df['Costo con Impuestos (USD)'] = (df['CIF (USD)'] + df['DDI (USD)'] + df['Tasas (USD)'] + 
                                      df['Antidumping (USD)'] + df['Ganancias (USD)'] + df['IIBB (USD)'] + 
                                      df['Agente (USD)'] + df['Despachante (USD)'])
    
    # Gastos fijos
    if 'Gastos Fijos por Producto (USD)' in df.columns:
        df['Costo Final por Producto (USD)'] = df['Costo con Impuestos (USD)'] + df['Gastos Fijos por Producto (USD)']
    else:
        df['Costo Final por Producto (USD)'] = df['Costo con Impuestos (USD)']
    
    # Precios unitarios
    df['Precio Unitario Final (USD)'] = df['Costo Final por Producto (USD)'] / df['Cantidad Total']
    df['Precio Unitario Final (Pesos)'] = df['Precio Unitario Final (USD)'] * precio_dolar
    
    # Porcentajes
    df['% del CBM'] = (df['CBM Total'] / total_cbm * 100).round(2)
    df['% del Peso'] = (df['Peso Total (kg)'] / total_peso * 100).round(2)
    df['% del Costo'] = (df['Costo Final por Producto (USD)'] / df['Costo Final por Producto (USD)'].sum() * 100).round(2)
    
    return df

def create_product_table(df_productos):
    """Crear tabla de productos con Dash DataTable"""
    if df_productos.empty:
        return html.Div("No hay productos agregados")
    
    # Preparar datos para la tabla
    columns = [
        {"name": "Producto", "id": "Nombre"},
        {"name": "Cantidad", "id": "Cantidad Total"},
        {"name": "CBM", "id": "CBM Total"},
        {"name": "FOB USD", "id": "FOB (USD)"},
        {"name": "Costo Final USD", "id": "Costo Final por Producto (USD)"},
        {"name": "Precio Unitario USD", "id": "Precio Unitario Final (USD)"},
        {"name": "Precio Unitario ARS", "id": "Precio Unitario Final (Pesos)"}
    ]
    
    # Formatear datos
    data = []
    for _, row in df_productos.iterrows():
        data.append({
            "Nombre": row.get('Nombre', ''),
            "Cantidad Total": f"{row.get('Cantidad Total', 0):,.0f}",
            "CBM Total": f"{row.get('CBM Total', 0):.4f}",
            "FOB (USD)": f"${row.get('FOB (USD)', 0):,.2f}",
            "Costo Final por Producto (USD)": f"${row.get('Costo Final por Producto (USD)', 0):,.2f}",
            "Precio Unitario Final (USD)": f"${row.get('Precio Unitario Final (USD)', 0):,.2f}",
            "Precio Unitario Final (Pesos)": f"${row.get('Precio Unitario Final (Pesos)', 0):,.2f}"
        })
    
    return dash.dash_table.DataTable(
        id='product-table',
        columns=columns,
        data=data,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
        ],
        page_size=10
    )

def create_summary_cards(df_productos, precio_dolar):
    """Crear tarjetas de resumen"""
    if df_productos.empty:
        return html.Div("No hay datos para mostrar")
    
    total_cbm = df_productos['CBM Total'].sum()
    total_peso = df_productos['Peso Total (kg)'].sum()
    total_costo_usd = df_productos['Costo Final por Producto (USD)'].sum()
    total_costo_ars = total_costo_usd * precio_dolar
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_cbm:.2f}", className="card-title text-center"),
                    html.P("Total CBM", className="card-text text-center")
                ])
            ], color="primary", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_peso:,.0f}", className="card-title text-center"),
                    html.P("Total Peso (kg)", className="card-text text-center")
                ])
            ], color="success", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${total_costo_usd:,.0f}", className="card-title text-center"),
                    html.P("Costo Total USD", className="card-text text-center")
                ])
            ], color="warning", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${total_costo_ars:,.0f}", className="card-title text-center"),
                    html.P("Costo Total ARS", className="card-text text-center")
                ])
            ], color="danger", outline=True)
        ], width=3)
    ]) 