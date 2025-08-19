import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def procesar_ventas_mercadolibre():
    st.title("📊 Análisis de Ventas MercadoLibre")
    st.markdown("---")
    
    # Configuración de la página
    st.set_page_config(
        page_title="Análisis Ventas ML",
        page_icon="📊",
        layout="wide"
    )
    
    # Cargar el archivo CSV
    try:
        # Leer el archivo CSV - usar la línea 5 como encabezados (índice 4)
        df = pd.read_csv('20250704_Ventas_AR_Mercado_Libre_y_Mercado_Shops_2025-07-04_20-02hs_2152194966.csv', 
                        header=4,  # Usar la línea 5 (índice 4) como encabezados
                        encoding='utf-8')
        
        st.success("✅ Archivo CSV cargado exitosamente")
        
        # Mostrar información básica del archivo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de registros", len(df))
        with col2:
            st.metric("Columnas disponibles", len(df.columns))
        with col3:
            ventas_entregadas = len(df[df['Estado'] == 'Entregado'])
            st.metric("Ventas entregadas", ventas_entregadas)
        
        # Seleccionar solo las columnas necesarias
        columnas_necesarias = [
            '# de venta',
            'Fecha de venta', 
            'Estado',
            'Unidades',
            'Ingresos por productos (ARS)',
            'Cargo por venta',
            'Costo fijo',
            'Ingresos por envío (ARS)',
            'Costos de envío (ARS)',
            'Impostos',
            'Total (ARS)',
            'Mes de facturación de tus cargos',
            'SKU',
            'Título de la publicación',
            'Precio unitario de venta de la publicación (ARS)',
            'Canal de venta'
        ]
        
        # Filtrar columnas que existen en el archivo
        columnas_existentes = [col for col in columnas_necesarias if col in df.columns]
        df_filtrado = df[columnas_existentes].copy()
        
        st.info(f"📋 Columnas seleccionadas: {len(columnas_existentes)} de {len(columnas_necesarias)}")
        
        # Limpiar y procesar datos
        df_filtrado = limpiar_datos(df_filtrado)
        
        # Filtrar solo ventas entregadas
        df_entregadas = df_filtrado[df_filtrado['Estado'] == 'Entregado'].copy()
        
        if len(df_entregadas) > 0:
            # Calcular ganancia neta
            df_entregadas = calcular_ganancia_neta(df_entregadas)
            
            # Mostrar resultados
            mostrar_resultados(df_entregadas)
        else:
            st.warning("⚠️ No se encontraron ventas entregadas en el archivo")
            
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.info("💡 Asegúrate de que el archivo CSV esté en el directorio correcto")

def limpiar_datos(df):
    """Limpiar y procesar los datos del DataFrame"""
    
    # Convertir columnas numéricas
    columnas_numericas = [
        'Unidades',
        'Ingresos por productos (ARS)',
        'Cargo por venta', 
        'Costo fijo',
        'Ingresos por envío (ARS)',
        'Costos de envío (ARS)',
        'Impostos',
        'Total (ARS)',
        'Precio unitario de venta de la publicación (ARS)'
    ]
    
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Limpiar valores negativos (convertir a positivos para cálculos)
    for col in ['Cargo por venta', 'Costo fijo', 'Costos de envío (ARS)', 'Impostos']:
        if col in df.columns:
            df[col] = df[col].abs()
    
    # Procesar fecha de venta
    if 'Fecha de venta' in df.columns:
        df['Fecha de venta'] = pd.to_datetime(df['Fecha de venta'], format='%d de %B de %Y %H:%M hs.', errors='coerce')
        df['Mes'] = df['Fecha de venta'].dt.strftime('%Y-%m')
    
    return df

def calcular_ganancia_neta(df):
    """Calcular la ganancia neta de cada venta"""
    
    # Fórmula de ganancia neta:
    # Ganancia = Total recibido - Costos totales
    # Costos totales = Comisión ML + Costo fijo + Costos de envío + Impuestos
    
    df['Comisión_ML'] = df['Cargo por venta'].replace([np.nan, None], 0)
    df['Costo_Fijo'] = df['Costo fijo'].replace([np.nan, None], 0)
    df['Costos_Envío'] = df['Costos de envío (ARS)'].replace([np.nan, None], 0)
    df['Impuestos_Adicionales'] = df['Impostos'].replace([np.nan, None], 0)
    df['Ingresos_Envío'] = df['Ingresos por envío (ARS)'].replace([np.nan, None], 0)
    
    # Calcular costos totales
    df['Costos_Total'] = (df['Comisión_ML'] + 
                         df['Costo_Fijo'] + 
                         df['Costos_Envío'] + 
                         df['Impuestos_Adicionales'])
    
    # Calcular ganancia neta
    df['Ganancia_Neta'] = df['Total (ARS)'] - df['Costos_Total']
    
    # Calcular margen de ganancia (%)
    df['Margen_Ganancia_%'] = np.where(
        df['Total (ARS)'] > 0,
        (df['Ganancia_Neta'] / df['Total (ARS)']) * 100,
        0
    )
    
    # Calcular ganancia por unidad
    df['Ganancia_por_Unidad'] = np.where(
        df['Unidades'] > 0,
        df['Ganancia_Neta'] / df['Unidades'],
        0
    )
    
    return df

def mostrar_resultados(df):
    """Mostrar los resultados del análisis"""
    
    st.markdown("## 📈 Resumen de Ventas Entregadas")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ventas = len(df)
        st.metric("Total Ventas", total_ventas)
    
    with col2:
        total_ingresos = df['Total (ARS)'].sum()
        st.metric("Total Ingresos", f"${total_ingresos:,.0f}")
    
    with col3:
        total_ganancia = df['Ganancia_Neta'].sum()
        st.metric("Ganancia Total", f"${total_ganancia:,.0f}")
    
    with col4:
        margen_promedio = df['Margen_Ganancia_%'].mean()
        st.metric("Margen Promedio", f"{margen_promedio:.1f}%")
    
    st.markdown("---")
    
    # Tabla detallada de ventas
    st.markdown("### 📋 Detalle de Ventas")
    
    # Seleccionar columnas para mostrar
    columnas_mostrar = [
        '# de venta',
        'Fecha de venta',
        'SKU',
        'Título de la publicación',
        'Unidades',
        'Total (ARS)',
        'Ganancia_Neta',
        'Margen_Ganancia_%',
        'Ganancia_por_Unidad'
    ]
    
    columnas_existentes = [col for col in columnas_mostrar if col in df.columns]
    df_mostrar = df[columnas_existentes].copy()
    
    # Formatear columnas numéricas
    if 'Total (ARS)' in df_mostrar.columns:
        df_mostrar['Total (ARS)'] = df_mostrar['Total (ARS)'].apply(lambda x: f"${x:,.0f}")
    if 'Ganancia_Neta' in df_mostrar.columns:
        df_mostrar['Ganancia_Neta'] = df_mostrar['Ganancia_Neta'].apply(lambda x: f"${x:,.0f}")
    if 'Margen_Ganancia_%' in df_mostrar.columns:
        df_mostrar['Margen_Ganancia_%'] = df_mostrar['Margen_Ganancia_%'].apply(lambda x: f"{x:.1f}%")
    if 'Ganancia_por_Unidad' in df_mostrar.columns:
        df_mostrar['Ganancia_por_Unidad'] = df_mostrar['Ganancia_por_Unidad'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(df_mostrar, use_container_width=True)
    
    # Gráficos
    st.markdown("---")
    st.markdown("### 📊 Análisis Gráfico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de ganancia por venta
        fig_ganancia = px.bar(
            df, 
            x='# de venta', 
            y='Ganancia_Neta',
            title='Ganancia Neta por Venta',
            labels={'Ganancia_Neta': 'Ganancia Neta (ARS)', '# de venta': 'Número de Venta'}
        )
        fig_ganancia.update_layout(height=400)
        st.plotly_chart(fig_ganancia, use_container_width=True)
    
    with col2:
        # Gráfico de margen de ganancia
        fig_margen = px.scatter(
            df,
            x='Total (ARS)',
            y='Margen_Ganancia_%',
            title='Margen de Ganancia vs Total de Venta',
            labels={'Total (ARS)': 'Total de Venta (ARS)', 'Margen_Ganancia_%': 'Margen (%)'}
        )
        fig_margen.update_layout(height=400)
        st.plotly_chart(fig_margen, use_container_width=True)
    
    # Resumen por mes
    if 'Mes' in df.columns:
        st.markdown("### 📅 Resumen Mensual")
        
        resumen_mensual = df.groupby('Mes').agg({
            'Total (ARS)': 'sum',
            'Ganancia_Neta': 'sum',
            'Unidades': 'sum',
            '# de venta': 'count'
        }).reset_index()
        
        resumen_mensual['Margen_Mensual_%'] = (resumen_mensual['Ganancia_Neta'] / resumen_mensual['Total (ARS)']) * 100
        
        # Formatear para mostrar
        resumen_mostrar = resumen_mensual.copy()
        resumen_mostrar['Total (ARS)'] = resumen_mostrar['Total (ARS)'].apply(lambda x: f"${x:,.0f}")
        resumen_mostrar['Ganancia_Neta'] = resumen_mostrar['Ganancia_Neta'].apply(lambda x: f"${x:,.0f}")
        resumen_mostrar['Margen_Mensual_%'] = resumen_mostrar['Margen_Mensual_%'].apply(lambda x: f"{x:.1f}%")
        resumen_mostrar['# de venta'] = resumen_mostrar['# de venta'].astype(int)
        
        st.dataframe(resumen_mostrar, use_container_width=True)
    
    # Botón para descargar resultados
    st.markdown("---")
    st.markdown("### 💾 Descargar Resultados")
    
    # Preparar datos para descarga
    df_descarga = df.copy()
    if 'Fecha de venta' in df_descarga.columns:
        df_descarga['Fecha de venta'] = df_descarga['Fecha de venta'].dt.strftime('%Y-%m-%d %H:%M')
    
    csv = df_descarga.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Descargar CSV con análisis completo",
        data=csv,
        file_name="analisis_ventas_mercadolibre.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    procesar_ventas_mercadolibre() 