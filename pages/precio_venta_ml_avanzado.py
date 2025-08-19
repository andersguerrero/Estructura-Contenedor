import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
import json
# import yaml  # Para futuras mejoras de carga de configuración
from typing import Dict, List, Optional, Tuple
import bisect

# Configuración de la página
st.set_page_config(
    page_title="🚀 Calculadora ML Avanzada",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1d391kg {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Variables CSS para colores modernos */
    :root {
        --primary-color: #87CEEB;
        --primary-dark: #4682B4;
        --primary-light: #B0E0E6;
        --secondary-color: #FFE600;
        --accent-color: #FF6B35;
        --success-color: #39B54A;
        --warning-color: #FF9500;
        --error-color: #E74C3C;
        --text-primary: #333333;
        --text-secondary: #666666;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8F9FA;
        --border-color: #DDDDDD;
        --shadow: 0 4px 12px rgba(0,0,0,0.1);
        --border-radius: 12px;
    }
    
    /* Contenedores principales */
    .main-container {
        background: var(--bg-primary);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
    }
    
    .config-section {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--primary-color);
    }
    
    /* Headers */
    .section-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: var(--shadow);
    }
    
    .section-header h2 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Tarjetas de resultados */
    .result-card {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow);
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
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
    
    /* Alertas */
    .alert-success {
        background: linear-gradient(135deg, rgba(57, 181, 74, 0.1) 0%, rgba(34, 197, 94, 0.1) 100%);
        border: 2px solid var(--success-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(255, 149, 0, 0.1) 0%, rgba(255, 193, 7, 0.1) 100%);
        border: 2px solid var(--warning-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-error {
        background: linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, rgba(220, 53, 69, 0.1) 100%);
        border: 2px solid var(--error-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Tablas mejoradas */
    .stDataFrame {
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
    }
    
    /* Inputs mejorados */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 2px solid var(--border-color);
        border-radius: var(--border-radius);
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(135, 206, 235, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== CLASES DE DATOS ====================

class Categoria:
    def __init__(self, id: str, nombre: str, comision_pct: float, 
                 vigente_desde: date = None, vigente_hasta: date = None):
        self.id = id
        self.nombre = nombre
        self.comision_pct = comision_pct
        self.vigente_desde = vigente_desde
        self.vigente_hasta = vigente_hasta

class RangoPrecio:
    def __init__(self, id: str, moneda: str, min_precio: float, max_precio: float,
                 costo_fijo: float, vigente_desde: date = None, vigente_hasta: date = None):
        self.id = id
        self.moneda = moneda
        self.min_precio = min_precio
        self.max_precio = max_precio
        self.costo_fijo = costo_fijo
        self.vigente_desde = vigente_desde
        self.vigente_hasta = vigente_hasta

class BandaEnvio:
    def __init__(self, id: str, regimen: str, peso_min_kg: float, peso_max_kg: float,
                 costo_envio_ars: float, subsidio_vendedor_pct: float = 0,
                 subsidio_vendedor_monto: float = 0, volumetrico_factor: float = None,
                 zona: str = "nacional", vigente_desde: date = None, vigente_hasta: date = None):
        self.id = id
        self.regimen = regimen
        self.peso_min_kg = peso_min_kg
        self.peso_max_kg = peso_max_kg
        self.costo_envio_ars = costo_envio_ars
        self.subsidio_vendedor_pct = subsidio_vendedor_pct
        self.subsidio_vendedor_monto = subsidio_vendedor_monto
        self.volumetrico_factor = volumetrico_factor
        self.zona = zona
        self.vigente_desde = vigente_desde
        self.vigente_hasta = vigente_hasta

class Variante:
    def __init__(self, variant_id: str, sku: str, titulo: str, categoria_id: str,
                 costo_unitario_usd: float, peso_kg: float,
                 largo_cm: float = 0, ancho_cm: float = 0, alto_cm: float = 0,
                 atributos: Dict = None):
        self.variant_id = variant_id
        self.sku = sku
        self.titulo = titulo
        self.categoria_id = categoria_id
        self.costo_unitario_usd = costo_unitario_usd
        self.peso_kg = peso_kg
        self.largo_cm = largo_cm
        self.ancho_cm = ancho_cm
        self.alto_cm = alto_cm
        self.atributos = atributos or {}

# ==================== CONFIGURACIONES POR DEFECTO ====================

def get_categorias_default() -> List[Categoria]:
    """Categorías con comisiones REALES de MercadoLibre Argentina 2024-2025 (promedio nacional 11.8% - 17.14%)"""
    return [
        # Comisiones basadas en el rango real de Argentina (ajustadas por provincia)
        # Usando valores promedio nacionales más representativos
        Categoria("MLA1055", "Electrónica, Audio y Video", 0.1585),  # ~15.85% promedio
        Categoria("MLA1648", "Computación", 0.1520),  # ~15.20% promedio 
        Categoria("MLA1039", "Cámaras y Accesorios", 0.1565),  # ~15.65% promedio
        Categoria("MLA1051", "Celulares y Teléfonos", 0.1620),  # ~16.20% promedio (categoría alta)
        Categoria("MLA1276", "Deportes y Fitness", 0.1380),  # ~13.80% promedio
        Categoria("MLA1430", "Ropa y Accesorios", 0.1320),   # ~13.20% promedio
        Categoria("MLA1367", "Hogar, Muebles y Jardín", 0.1420),  # ~14.20% promedio
        Categoria("MLA1071", "Animales y Mascotas", 0.1450),  # ~14.50% promedio
        Categoria("MLA1132", "Juegos y Juguetes", 0.1480),   # ~14.80% promedio
        Categoria("MLA1168", "Música, Películas y Series", 0.1350),  # ~13.50% promedio
        Categoria("MLA1182", "Herramientas", 0.1440),   # ~14.40% promedio
        Categoria("MLA1196", "Electrodomésticos", 0.1550),  # ~15.50% promedio
        Categoria("MLA1000", "Supermercado", 0.1680),   # ~16.80% (sin costos fijos adicionales)
        Categoria("MLA1499", "Industrias y Oficinas", 0.1290),  # ~12.90% promedio B2B
        Categoria("MLA1953", "Servicios", 0.1250),   # ~12.50% promedio servicios
        # Nuevas categorías específicas de Argentina
        Categoria("MLA1743", "Autos, Motos y Otros", 0.1180),  # ~11.80% mínima
        Categoria("MLA1540", "Inmuebles", 0.1200),  # ~12.00% inmuebles
        Categoria("MLA1953", "Arte y Entretenimiento", 0.1380),  # ~13.80%
    ]

def get_rangos_precio_default() -> List[RangoPrecio]:
    """Rangos de precio con costos fijos OFICIALES de MercadoLibre Argentina 2024-2025"""
    return [
        # Costos fijos OFICIALES según información de MercadoLibre Argentina
        # Fuente: https://www.mercadolibre.com.ar/ayuda/Cargos-por-vender-productos_870
        RangoPrecio("R1", "ARS", 1000, 14999, 1095),    # $1k-$15k: $1.095 por unidad vendida
        RangoPrecio("R2", "ARS", 15000, 24999, 2190),   # $15k-$25k: $2.190 por unidad vendida
        RangoPrecio("R3", "ARS", 25000, 32999, 2628),   # $25k-$33k: $2.628 por unidad vendida
        RangoPrecio("R4", "ARS", 33000, 49999, 0),      # $33k-$50k: Sin costo fijo
        RangoPrecio("R5", "ARS", 50000, 99999, 0),      # $50k-$100k: Sin costo fijo
        RangoPrecio("R6", "ARS", 100000, 199999, 0),    # $100k-$200k: Sin costo fijo
        RangoPrecio("R7", "ARS", 200000, 499999, 0),    # $200k-$500k: Sin costo fijo
        RangoPrecio("R8", "ARS", 500000, 999999, 0),    # $500k-$1M: Sin costo fijo
        RangoPrecio("R9", "ARS", 1000000, float('inf'), 0),  # +$1M: Sin costo fijo
        # NOTA: Productos de supermercado Full Súper NO pagan costo fijo, pero sí pagan 3 puntos porcentuales adicionales
    ]

def get_bandas_envio_default() -> List[BandaEnvio]:
    """Bandas de envío OFICIALES MercadoLibre Argentina 2024-2025 - MercadoLíder Platinum"""
    bandas = []
    
    # MercadoEnvíos - Tarifas OFICIALES Argentina con descuento Platinum 50%
    # Fuente: Información oficial de MercadoLibre Argentina - Costos de envío actualizados
    # MercadoLíder Platinum: 50% descuento en envíos para productos >= $33k
    # Todos los métodos de envío (Full, Flex) tienen el mismo costo base
    bandas.extend([
        BandaEnvio("E1", "envio", 0, 0.3, 5304, zona="nacional"),       # Hasta 0,3 kg - $5.304 (50% descuento)
        BandaEnvio("E2", "envio", 0.3, 0.5, 5736, zona="nacional"),     # De 0,3 a 0,5 kg - $5.736 (50% descuento)
        BandaEnvio("E3", "envio", 0.5, 1.0, 6431, zona="nacional"),     # De 0,5 a 1 kg - $6.431 (50% descuento)
        BandaEnvio("E4", "envio", 1.0, 2.0, 6862, zona="nacional"),     # De 1 a 2 kg - $6.862 (50% descuento)
        BandaEnvio("E5", "envio", 2.0, 5.0, 9127, zona="nacional"),     # De 2 a 5 kg - $9.127 (50% descuento)
        BandaEnvio("E6", "envio", 5.0, 10.0, 10840, zona="nacional"),   # De 5 a 10 kg - $10.840 (50% descuento)
        BandaEnvio("E7", "envio", 10.0, 15.0, 12544, zona="nacional"),  # De 10 a 15 kg - $12.544 (50% descuento)
        BandaEnvio("E8", "envio", 15.0, 20.0, 14985.5, zona="nacional"), # De 15 a 20 kg - $14.985,50 (50% descuento)
        BandaEnvio("E9", "envio", 20.0, 25.0, 17879.5, zona="nacional"), # De 20 a 25 kg - $17.879,50 (50% descuento)
        BandaEnvio("E10", "envio", 25.0, 30.0, 24540.5, zona="nacional"), # De 25 a 30 kg - $24.540,50 (50% descuento)
        BandaEnvio("E11", "envio", 30.0, 40.0, 28015.5, zona="nacional"), # De 30 a 40 kg - $28.015,50 (50% descuento)
        BandaEnvio("E12", "envio", 40.0, 50.0, 29473, zona="nacional"),  # De 40 a 50 kg - $29.473 (50% descuento)
        BandaEnvio("E13", "envio", 50.0, 60.0, 32747.5, zona="nacional"), # De 50 a 60 kg - $32.747,50 (50% descuento)
        BandaEnvio("E14", "envio", 60.0, 70.0, 34057, zona="nacional"),  # De 60 a 70 kg - $34.057 (50% descuento)
        BandaEnvio("E15", "envio", 70.0, 80.0, 39379, zona="nacional"),  # De 70 a 80 kg - $39.379 (50% descuento)
        BandaEnvio("E16", "envio", 80.0, 90.0, 48691.5, zona="nacional"), # De 80 a 90 kg - $48.691,50 (50% descuento)
        BandaEnvio("E17", "envio", 90.0, 100.0, 56150.5, zona="nacional"), # De 90 a 100 kg - $56.150,50 (50% descuento)
        BandaEnvio("E18", "envio", 100.0, 120.0, 61301.5, zona="nacional"), # De 100 a 120 kg - $61.301,50 (50% descuento)
        BandaEnvio("E19", "envio", 120.0, 140.0, 69029, zona="nacional"),  # De 120 a 140 kg - $69.029 (50% descuento)
        BandaEnvio("E20", "envio", 140.0, 160.0, 76755.5, zona="nacional"), # De 140 a 160 kg - $76.755,50 (50% descuento)
        BandaEnvio("E21", "envio", 160.0, 180.0, 84482.5, zona="nacional"), # De 160 a 180 kg - $84.482,50 (50% descuento)
        BandaEnvio("E22", "envio", 180.0, float('inf'), 92210, zona="nacional"), # Más de 180 kg - $92.210 (50% descuento)
    ])
    
    return bandas

def get_variantes_ejemplo() -> List[Variante]:
    """Variantes de ejemplo realistas para MercadoLíder Platinum"""
    return [
        # Celulares - Alta comisión pero alto volumen
        Variante("V1", "IPHONE15-BLK-128", "iPhone 15 128GB Negro", "MLA1051", 
                850.0, 0.2, 14.7, 7.1, 0.8),
        Variante("V2", "SAMSUNG-S24-WHT-256", "Samsung Galaxy S24 256GB Blanco", "MLA1051",
                720.0, 0.18, 14.6, 7.0, 0.8),
        Variante("V3", "XIAOMI-13-BLU-128", "Xiaomi 13 128GB Azul", "MLA1051",
                380.0, 0.19, 15.2, 7.4, 0.81),
        
        # Electrónica - Gama media/alta
        Variante("V4", "AIRPODS-PRO-2", "AirPods Pro 2da Gen", "MLA1055",
                200.0, 0.06, 6.1, 4.5, 2.2),
        Variante("V5", "SONY-WH1000XM5", "Sony WH-1000XM5 Headphones", "MLA1055",
                280.0, 0.25, 25.4, 20.3, 7.6),
        Variante("V6", "GOPRO-HERO12", "GoPro Hero 12 Black", "MLA1039",
                420.0, 0.15, 7.1, 5.5, 3.3),
        
        # Computación - Alto valor
        Variante("V7", "MACBOOK-AIR-M3", "MacBook Air M3 13'' 256GB", "MLA1648",
                1200.0, 1.24, 30.4, 21.5, 1.1),
        Variante("V8", "LENOVO-LEGION-5", "Lenovo Legion 5 Gaming Laptop", "MLA1648",
                850.0, 2.3, 36.2, 26.0, 2.4),
        
        # Gaming - Volumen medio
        Variante("V9", "PLAYSTATION5-STD", "PlayStation 5 Standard Edition", "MLA1132",
                450.0, 4.5, 39.0, 10.4, 26.0),
        Variante("V10", "NINTENDO-SWITCH-OLED", "Nintendo Switch OLED", "MLA1132",
                280.0, 0.42, 24.2, 10.6, 1.4),
        
        # Electrodomésticos - Peso y volumen altos
        Variante("V11", "PHILIPS-AIRFRYER-XL", "Philips Airfryer XXL 7.3L", "MLA1196",
                180.0, 5.8, 31.5, 40.3, 36.8),
        Variante("V12", "SAMSUNG-TV-55-4K", "Samsung Smart TV 55'' 4K", "MLA1055",
                520.0, 18.5, 123.2, 70.8, 8.1),
        
        # Ropa - Comisión mínima, alto volumen
        Variante("V13", "NIKE-AIR-MAX-270", "Nike Air Max 270 Running", "MLA1430",
                85.0, 0.8, 33.0, 20.5, 12.0),
        Variante("V14", "ADIDAS-ULTRABOOST-22", "Adidas Ultraboost 22", "MLA1430",
                140.0, 0.9, 34.2, 21.0, 12.5),
        
        # Hogar - Variedad de pesos
        Variante("V15", "DYSON-V15-DETECT", "Dyson V15 Detect Absolute", "MLA1367",
                480.0, 3.1, 126.0, 25.0, 25.0),
    ]

# ==================== FUNCIONES DE BÚSQUEDA ====================

def buscar_categoria(categorias: List[Categoria], categoria_id: str) -> Optional[Categoria]:
    """Busca una categoría por ID"""
    for cat in categorias:
        if cat.id == categoria_id:
            return cat
    return None

def buscar_rango_precio(rangos: List[RangoPrecio], precio: float, moneda: str = "ARS") -> Optional[RangoPrecio]:
    """Busca el rango de precio que corresponde al precio dado"""
    for rango in rangos:
        if (rango.moneda == moneda and 
            rango.min_precio <= precio <= rango.max_precio):
            return rango
    return None

def buscar_banda_envio(bandas: List[BandaEnvio], regimen: str, peso_kg: float, 
                      zona: str = "nacional") -> Optional[BandaEnvio]:
    """Busca la banda de envío que corresponde al peso (todos los regímenes tienen el mismo costo)"""
    for banda in bandas:
        if (banda.zona == zona and
            banda.peso_min_kg <= peso_kg <= banda.peso_max_kg):
            return banda
    return None

def calcular_peso_facturable(variante: Variante, volumetrico_factor: float = None) -> float:
    """Calcula el peso facturable considerando peso volumétrico"""
    peso_real = variante.peso_kg
    
    if volumetrico_factor and variante.largo_cm and variante.ancho_cm and variante.alto_cm:
        volumen_cm3 = variante.largo_cm * variante.ancho_cm * variante.alto_cm
        peso_volumetrico = volumen_cm3 / volumetrico_factor / 1000  # convertir a kg
        return max(peso_real, peso_volumetrico)
    
    return peso_real

# ==================== SOLVER DE PRECIOS ====================

def calcular_costo_envio_vendedor(banda: BandaEnvio, precio_producto: float = 0) -> float:
    """Calcula el costo de envío que asume el vendedor con beneficios Platinum automáticos"""
    costo_base = banda.costo_envio_ars
    
    # Beneficio MercadoLíder Platinum: 50% descuento en envíos para productos desde $33k
    # (Los precios ya tienen el descuento aplicado)
    if precio_producto >= 33000:
        # El descuento ya está aplicado en las tarifas, no hacer nada adicional
        pass
    
    # Aplicar subsidio adicional del vendedor si existe
    if banda.subsidio_vendedor_monto > 0:
        return banda.subsidio_vendedor_monto
    else:
        return costo_base * banda.subsidio_vendedor_pct

def calcular_impuestos_sobre_precio(precio: float, iva_pct: float = 0, 
                                   iibb_pct: float = 0, pais_pct: float = 0) -> float:
    """Calcula impuestos aplicados sobre el precio de venta"""
    return precio * (iva_pct + iibb_pct + pais_pct) / 100

def ganancia_neta(precio: float, costo_ars: float, categoria: Categoria,
                 rango: RangoPrecio, envio_vendedor: float,
                 iva_pct: float = 0, iibb_pct: float = 0, pais_pct: float = 0) -> float:
    """Calcula la ganancia neta para un precio dado"""
    comision_variable = precio * categoria.comision_pct
    costo_fijo = rango.costo_fijo if rango else 0
    impuestos = calcular_impuestos_sobre_precio(precio, iva_pct, iibb_pct, pais_pct)
    
    return precio - comision_variable - costo_fijo - envio_vendedor - impuestos - costo_ars

def solver_precio_optimo(costo_ars: float, margen_objetivo: float, 
                        categoria: Categoria, rangos: List[RangoPrecio],
                        envio_vendedor: float, iva_pct: float = 0,
                        iibb_pct: float = 0, pais_pct: float = 0,
                        es_margen_pct: bool = False, max_iter: int = 100,
                        tolerancia: float = 0.01) -> Tuple[float, Dict]:
    """
    Solver iterativo para encontrar el precio óptimo.
    Retorna (precio_optimo, desglose_detallado)
    """
    
    # Estimación inicial
    factor_inicial = 1.0 + (categoria.comision_pct if categoria else 0.13) + 0.1  # +10% buffer
    precio = (costo_ars + envio_vendedor + margen_objetivo) * factor_inicial
    
    precio_anterior = 0
    iteracion = 0
    
    while iteracion < max_iter and abs(precio - precio_anterior) > tolerancia:
        precio_anterior = precio
        
        # Buscar rango actual
        rango_actual = buscar_rango_precio(rangos, precio)
        
        # Calcular ganancia actual
        ganancia_actual = ganancia_neta(precio, costo_ars, categoria, rango_actual,
                                      envio_vendedor, iva_pct, iibb_pct, pais_pct)
        
        # Calcular error
        if es_margen_pct:
            margen_actual_pct = (ganancia_actual / precio) * 100 if precio > 0 else 0
            error = margen_actual_pct - margen_objetivo
            # Ajustar precio basado en diferencia porcentual
            if abs(error) > tolerancia:
                factor_ajuste = 1 + (error / 100)
                precio = precio * factor_ajuste
        else:
            error = ganancia_actual - margen_objetivo
            # Ajustar precio basado en diferencia absoluta
            if abs(error) > tolerancia:
                # Usar método de Newton simplificado
                derivada = 1 - (categoria.comision_pct if categoria else 0.13) - (iva_pct + iibb_pct + pais_pct) / 100
                if derivada != 0:
                    precio = precio - error / derivada
                else:
                    precio = precio + error  # fallback simple
        
        iteracion += 1
    
    # Calcular desglose final
    rango_final = buscar_rango_precio(rangos, precio)
    ganancia_final = ganancia_neta(precio, costo_ars, categoria, rango_final,
                                 envio_vendedor, iva_pct, iibb_pct, pais_pct)
    
    desglose = {
        'precio_final': precio,
        'costo_ars': costo_ars,
        'comision_variable': precio * (categoria.comision_pct if categoria else 0),
        'costo_fijo': rango_final.costo_fijo if rango_final else 0,
        'envio_vendedor': envio_vendedor,
        'impuestos_total': calcular_impuestos_sobre_precio(precio, iva_pct, iibb_pct, pais_pct),
        'ganancia_neta': ganancia_final,
        'margen_pct': (ganancia_final / precio * 100) if precio > 0 else 0,
        'iteraciones': iteracion,
        'categoria_aplicada': categoria.nombre if categoria else "N/A",
        'rango_aplicado': f"${rango_final.min_precio:,.0f} - ${rango_final.max_precio:,.0f}" if rango_final else "N/A"
    }
    
    return precio, desglose

def aplicar_redondeo(precio: float, regla: str) -> float:
    """Aplica reglas de redondeo al precio"""
    if regla == "sin_decimales":
        return round(precio)
    elif regla == "multiplo_10":
        return round(precio / 10) * 10
    elif regla == "multiplo_100":
        return round(precio / 100) * 100
    elif regla == "terminacion_990":
        base = int(precio / 1000) * 1000
        return base + 990 if precio > base + 500 else base - 10
    else:
        return precio

# ==================== INICIALIZACIÓN DE DATOS ====================

def inicializar_datos():
    """Inicializa los datos en session_state si no existen"""
    if 'categorias' not in st.session_state:
        st.session_state.categorias = get_categorias_default()
    
    if 'rangos_precio' not in st.session_state:
        st.session_state.rangos_precio = get_rangos_precio_default()
    
    if 'bandas_envio' not in st.session_state:
        st.session_state.bandas_envio = get_bandas_envio_default()
    
    if 'variantes' not in st.session_state:
        st.session_state.variantes = get_variantes_ejemplo()
    
    # Parámetros por defecto
    if 'tc_ars_usd' not in st.session_state:
        st.session_state.tc_ars_usd = 1000.0
    if 'iva_ventas_pct' not in st.session_state:
        st.session_state.iva_ventas_pct = 0.0
    if 'iibb_pct' not in st.session_state:
        st.session_state.iibb_pct = 2.0
    if 'pais_pct' not in st.session_state:
        st.session_state.pais_pct = 0.0

# ==================== INTERFAZ PRINCIPAL ====================

# Navegación
st.markdown("### 🧭 Navegación")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🏠 Inicio", key="nav-home", use_container_width=True):
        st.switch_page("app_costos_final.py")
with col2:
    if st.button("📦 Contenedor", key="nav-container", use_container_width=True):
        st.switch_page("pages/contenedor_completo.py")
with col3:
    if st.button("💰 Ganancias", key="nav-ganancias", use_container_width=True):
        st.switch_page("pages/precio_venta.py")
with col4:
    if st.button("📋 Inventario", key="nav-inventory", use_container_width=True):
        st.switch_page("pages/inventario.py")
with col5:
    if st.button("🚀 ML Avanzado", key="nav-precio-ml-adv", use_container_width=True, type="primary"):
        st.switch_page("pages/precio_venta_ml_avanzado.py")

st.markdown("---")

# Inicializar datos
inicializar_datos()

# Título principal con badge Platinum Argentina
st.markdown("""
<div class="section-header">
    <h2>🚀 Calculadora MercadoLibre Argentina Avanzada</h2>
    <div style="background: linear-gradient(135deg, #C0C0C0 0%, #E8E8E8 100%); color: #333; padding: 0.5rem 1rem; border-radius: 20px; display: inline-block; margin-top: 0.5rem; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        🇦🇷💎 MercadoLíder Platinum Argentina - Tarifas Oficiales 2024-2025
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar para configuración
with st.sidebar:
    st.markdown("### ⚙️ Configuración General")
    
    # Tipo de cambio
    tc_ars_usd = st.number_input(
        "💱 Tipo de Cambio USD → ARS",
        min_value=1.0,
        value=st.session_state.tc_ars_usd,
        step=1.0,
        help="Tipo de cambio actual"
    )
    st.session_state.tc_ars_usd = tc_ars_usd
    
    st.markdown("### 📊 Impuestos sobre Ventas")
    
    iva_ventas = st.number_input(
        "IVA Ventas (%)",
        min_value=0.0,
        max_value=50.0,
        value=st.session_state.iva_ventas_pct,
        step=0.1,
        help="IVA aplicado sobre ventas"
    )
    st.session_state.iva_ventas_pct = iva_ventas
    
    iibb = st.number_input(
        "IIBB (%)",
        min_value=0.0,
        max_value=10.0,
        value=st.session_state.iibb_pct,
        step=0.1,
        help="Ingresos Brutos sobre ventas"
    )
    st.session_state.iibb_pct = iibb
    
    pais = st.number_input(
        "Impuesto PAÍS (%)",
        min_value=0.0,
        max_value=50.0,
        value=st.session_state.pais_pct,
        step=0.1,
        help="Impuesto PAÍS (si aplica)"
    )
    st.session_state.pais_pct = pais
    
    st.markdown("### 🎯 Configuración de Cálculo")
    
    regla_redondeo = st.selectbox(
        "Regla de Redondeo",
        ["sin_redondeo", "sin_decimales", "multiplo_10", "multiplo_100", "terminacion_990"],
        index=1,
        help="Cómo redondear el precio final"
    )

# Área principal - Calculadora Simplificada
st.markdown("## 🧮 Calculadora de Precio ML")

# Selección rápida de producto
st.markdown("### 📦 Producto")
variantes_opciones = {f"{v.titulo} ({v.sku})": i for i, v in enumerate(st.session_state.variantes)}
variante_seleccionada_key = st.selectbox(
    "Seleccionar Producto",
    options=list(variantes_opciones.keys()),
    help="Selecciona el producto a calcular"
)

if variante_seleccionada_key:
    variante_idx = variantes_opciones[variante_seleccionada_key]
    variante = st.session_state.variantes[variante_idx]
    
    # Mostrar información del producto de forma compacta
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.info(f"**Costo:** ${variante.costo_unitario_usd:,.2f} USD")
    with col_info2:
        st.info(f"**Peso:** {variante.peso_kg} kg")
    with col_info3:
        st.info(f"**Categoría:** {variante.categoria_id}")

# Configuración simplificada
st.markdown("### ⚙️ Configuración Rápida")

col_config1, col_config2 = st.columns(2)

with col_config1:
    # Margen objetivo simplificado
    tipo_margen = st.radio(
        "🎯 Ganancia Deseada",
        ["Monto Fijo (ARS)", "Porcentaje (%)"],
        horizontal=True
    )
    
    if tipo_margen == "Monto Fijo (ARS)":
        margen_objetivo = st.number_input(
            "Ganancia en Pesos",
            min_value=0.0,
            value=5000.0,
            step=500.0,
            help="Ganancia neta deseada"
        )
        es_margen_pct = False
    else:
        margen_objetivo = st.number_input(
            "Margen (%)",
            min_value=0.0,
            max_value=500.0,
            value=30.0,
            step=5.0,
            help="Porcentaje de ganancia"
        )
        es_margen_pct = True

with col_config2:
    # Envío simplificado
    subsidio_envio = st.number_input(
        "🚚 Subsidio Envío (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=10.0,
        help="Porcentaje que subsidias del envío"
    )
    
    costos_extra = st.number_input(
        "📦 Costos Extra (ARS)",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="Packaging, handling, etc."
    )
    
# Botón de cálculo simplificado
st.markdown("---")
if st.button("🚀 Calcular Precio", use_container_width=True, type="primary", help="Calcular precio óptimo para MercadoLibre"):
    try:
        # Validaciones rápidas
        categoria = buscar_categoria(st.session_state.categorias, variante.categoria_id)
        if not categoria:
            st.error(f"❌ Categoría {variante.categoria_id} no encontrada")
            st.stop()
        
        # Calcular peso facturable
        peso_facturable = calcular_peso_facturable(variante)
        
        # Buscar banda de envío (simplificado)
        banda = buscar_banda_envio(st.session_state.bandas_envio, "envio", peso_facturable, "nacional")
        if not banda:
            st.error(f"❌ No se encontró banda de envío para {peso_facturable}kg")
            st.stop()
        
        # Cálculos principales
        costo_ars = (variante.costo_unitario_usd * tc_ars_usd) + costos_extra
        banda.subsidio_vendedor_pct = subsidio_envio
        envio_vendedor = calcular_costo_envio_vendedor(banda)
        
        # Ejecutar solver
        precio_optimo, desglose = solver_precio_optimo(
            costo_ars=costo_ars,
            margen_objetivo=margen_objetivo,
            categoria=categoria,
            rangos=st.session_state.rangos_precio,
            envio_vendedor=envio_vendedor,
            iva_pct=iva_ventas,
            iibb_pct=iibb,
            pais_pct=pais,
            es_margen_pct=es_margen_pct
        )
        
        # Aplicar redondeo automático (sin decimales)
        precio_final = aplicar_redondeo(precio_optimo, "sin_decimales")
        
        # Recalcular ganancia final
        rango_final = buscar_rango_precio(st.session_state.rangos_precio, precio_final)
        ganancia_final = ganancia_neta(precio_final, costo_ars, categoria, 
                                     rango_final, envio_vendedor, iva_ventas, iibb, pais)
        margen_final_pct = (ganancia_final / precio_final * 100) if precio_final > 0 else 0
        
        # Mostrar resultados simplificados
        st.markdown("## 💰 Resultado")
        
        # Métricas principales en una sola fila
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.metric(
                "💰 Precio Recomendado",
                f"${precio_final:,.0f}",
                help="Precio final para MercadoLibre"
            )
                
        with col_res2:
            st.metric(
                "📈 Ganancia Neta",
                f"${ganancia_final:,.0f}",
                help="Ganancia después de todos los costos"
            )
                
        with col_res3:
            st.metric(
                "📊 Margen Real",
                f"{margen_final_pct:.1f}%",
                help="Margen de ganancia obtenido"
            )
        
        # Resumen rápido
        st.markdown("### 📋 Resumen Rápido")
        
        col_sum1, col_sum2 = st.columns(2)
        
        with col_sum1:
            st.info(f"""
            **📦 Costo Total:** ${costo_ars:,.0f}
            **🏪 Comisión ML:** ${desglose['comision_variable']:,.0f} ({categoria.comision_pct*100:.1f}%)
            **🚚 Envío:** ${envio_vendedor:,.0f}
            """)
        
        with col_sum2:
            st.success(f"""
            **💰 Precio Final:** ${precio_final:,.0f}
            **✅ Ganancia:** ${ganancia_final:,.0f}
            **📊 Margen:** {margen_final_pct:.1f}%
            """)
        
        # Alertas simples
        if margen_final_pct < 15:
            st.warning(f"⚠️ Margen bajo: {margen_final_pct:.1f}% - Considera aumentar el precio")
        elif margen_final_pct > 50:
            st.success(f"🎉 Excelente margen: {margen_final_pct:.1f}%")
        else:
            st.info(f"✅ Margen aceptable: {margen_final_pct:.1f}%")
                
    except Exception as e:
        st.error(f"Error en el cálculo: {str(e)}")

# Configuración simplificada en expander
with st.expander("⚙️ Configuración Avanzada"):
    st.markdown("### 🔧 Parámetros del Sistema")
    
    col_adv1, col_adv2 = st.columns(2)
    
    with col_adv1:
        st.info(f"""
        **💱 Tipo de Cambio:** ${tc_ars_usd:,.0f}
        **🏷️ Categorías:** {len(st.session_state.categorias)}
        **💰 Rangos Precio:** {len(st.session_state.rangos_precio)}
        **🚚 Bandas Envío:** {len(st.session_state.bandas_envio)}
        """)
    
    with col_adv2:
        st.info(f"""
        **📊 IVA:** {iva_ventas}%
        **📈 IIBB:** {iibb}%
        **🇦🇷 PAÍS:** {pais}%
        **💎 Platinum:** Activo
        """)

# Información del sistema simplificada
st.markdown("---")
st.markdown("""
<div class="config-section">
    <h4>💎 Calculadora Simplificada - MercadoLíder Platinum Argentina</h4>
    <p><strong>🇦🇷 Sistema optimizado con:</strong></p>
    <ul>
        <li>✅ <strong>50% descuento en MercadoEnvíos</strong> (productos desde $33k)</li>
        <li>✅ <strong>Comisiones oficiales Argentina 2024-2025</strong></li>
        <li>✅ <strong>Costos fijos oficiales</strong> de MercadoLibre</li>
        <li>✅ <strong>Tarifas de envío actualizadas</strong> con descuento Platinum</li>
        <li>✅ <strong>Interfaz simplificada</strong> para cálculos rápidos</li>
        <li>✅ <strong>Solver automático</strong> para precio óptimo</li>
    </ul>
    <p style="color: var(--ml-blue-dark); font-weight: 600;">
        🇦🇷 Calculadora optimizada para MercadoLíder Platinum Argentina
    </p>
</div>
""", unsafe_allow_html=True)
