# 📊 Sistema de Análisis de Costos y Ganancias

Sistema completo para análisis de costos de importación, gestión de inventario y análisis de ganancias de MercadoLibre.

## 🚀 Características Principales

### 📦 **Análisis de Costos Individual**
- Cálculo detallado de costos por producto
- Impuestos (DDI, IVA, Ganancias, IIBB)
- Análisis de contenedores
- Configuración flexible de parámetros

### 🏭 **Contenedor Completo**
- Análisis de contenedores con múltiples productos
- Optimización de espacio y costos
- Cálculos proporcionales automáticos

### 📋 **Gestión de Inventario**
- Carga masiva de productos
- Seguimiento de stock
- Análisis de rotación

### 💰 **Análisis de Ganancias**
- Procesamiento de reportes de MercadoLibre
- Cálculo de ganancias netas
- Análisis de rentabilidad

## 🛠️ Instalación

### Requisitos
- Python 3.8+
- pip

### Instalación Local
```bash
# Clonar repositorio
git clone <tu-repositorio>

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app_costos_final.py
```

## 🌐 Despliegue

### Streamlit Cloud (Recomendado)
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona este repositorio
4. Configura: `app_costos_final.py` como archivo principal
5. ¡Listo! Tu app estará en `https://TU_APP.streamlit.app`

## 📁 Estructura del Proyecto

```
├── app_costos_final.py          # Aplicación principal
├── app_dash.py                  # Dashboard alternativo
├── procesar_ventas_mercadolibre.py  # Procesador de reportes ML
├── pages/                       # Páginas adicionales
│   ├── contenedor_completo.py   # Análisis de contenedores
│   ├── inventario.py            # Gestión de inventario
│   ├── precio_venta.py          # Cálculo de precios
│   └── precio_venta_ml_avanzado.py  # Análisis avanzado ML
├── modules/                     # Módulos de funcionalidad
│   ├── contenedor_dash.py       # Dashboard de contenedores
│   ├── inventario_dash.py       # Dashboard de inventario
│   └── ganancias_dash.py        # Dashboard de ganancias
├── requirements.txt             # Dependencias
├── .streamlit/                  # Configuración de Streamlit
└── .gitignore                   # Archivos a ignorar
```

## 🎯 Uso Rápido

1. **Configurar parámetros** en el sidebar (precio del dólar, impuestos)
2. **Ingresar datos del producto** (precio FOB, dimensiones, peso)
3. **Calcular costos** para ver el análisis completo
4. **Agregar al contenedor** para análisis masivo
5. **Usar módulos adicionales** según necesidades

## 🔧 Configuración

### Parámetros Principales
- **Precio del Dólar**: Cotización actual
- **DDI**: Derechos de Importación
- **IVA**: Impuesto al Valor Agregado
- **Ganancias**: Impuesto a las Ganancias
- **IIBB**: Impuesto sobre Ingresos Brutos

### Archivos de Configuración
- `.streamlit/config.toml`: Configuración de Streamlit
- `requirements.txt`: Dependencias de Python

## 📊 Módulos Disponibles

### 1. Análisis Individual
- Cálculo por producto individual
- Análisis detallado de costos
- Configuración personalizada

### 2. Contenedor Completo
- Análisis de contenedores 40HQ
- Múltiples productos
- Optimización de espacio

### 3. Inventario
- Gestión de stock
- Carga masiva
- Seguimiento de productos

### 4. Ganancias ML
- Procesamiento de reportes
- Análisis de rentabilidad
- Cálculo de ganancias netas

## 🚀 Despliegue en Producción

### Opciones Recomendadas
1. **Streamlit Cloud** (Gratis, fácil)
2. **Railway** (Gratis, moderno)
3. **Heroku** (Pago, profesional)
4. **VPS** (Control total)

### Configuración Avanzada
- Dominio personalizado
- HTTPS automático
- Variables de entorno
- Autenticación (opcional)

## 📞 Soporte

Para ayuda con:
- Configuración del sistema
- Despliegue en producción
- Optimización de rendimiento
- Nuevas funcionalidades

## 📄 Licencia

Este proyecto está diseñado para uso comercial y personal.

---

**¡Tu sistema de análisis de costos está listo para usar! 🚀**
