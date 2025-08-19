#!/usr/bin/env python3
"""
Script de inicio rápido para el Sistema de Análisis de Costos
"""

import subprocess
import sys
import os

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    try:
        import streamlit
        import pandas
        import plotly
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Falta instalar dependencias: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        return False

def run_app():
    """Ejecutar la aplicación principal"""
    if not check_dependencies():
        return
    
    print("🚀 Iniciando Sistema de Análisis de Costos...")
    print("📊 Aplicación principal: app_costos_final.py")
    print("🌐 La aplicación estará disponible en: http://localhost:8501")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app_costos_final.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida")
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")

def run_dashboard():
    """Ejecutar el dashboard alternativo"""
    if not check_dependencies():
        return
    
    print("🚀 Iniciando Dashboard Alternativo...")
    print("📊 Dashboard: app_dash.py")
    print("🌐 Disponible en: http://localhost:8502")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app_dash.py",
            "--server.port=8502",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard detenido")
    except Exception as e:
        print(f"❌ Error al ejecutar el dashboard: {e}")

def main():
    """Función principal"""
    print("📊 Sistema de Análisis de Costos y Ganancias")
    print("=" * 50)
    print("1. Aplicación Principal (app_costos_final.py)")
    print("2. Dashboard Alternativo (app_dash.py)")
    print("3. Instalar dependencias")
    print("4. Salir")
    print("-" * 50)
    
    while True:
        try:
            choice = input("Selecciona una opción (1-4): ").strip()
            
            if choice == "1":
                run_app()
                break
            elif choice == "2":
                run_dashboard()
                break
            elif choice == "3":
                print("📦 Instalando dependencias...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("✅ Dependencias instaladas")
                break
            elif choice == "4":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
