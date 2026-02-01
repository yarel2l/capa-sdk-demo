#!/bin/bash

# Script de inicio rápido para el demo de CAPA con Reflex

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 CAPA SDK Demo - Reflex"
echo "=========================="
echo ""
echo "📂 Directorio: $SCRIPT_DIR"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No se detectó un entorno virtual activado"
    echo "   Activando entorno virtual del proyecto padre..."
    cd ..
    source .venv/bin/activate
    cd demo_reflex
fi

# Check if reflex is installed
if ! command -v reflex &> /dev/null; then
    echo "📦 Instalando Reflex y dependencias..."
    pip install -r requirements.txt
fi

# Create necessary directories
echo "📁 Creando directorios necesarios..."
mkdir -p uploaded_images exports assets

# Initialize reflex if needed
if [ ! -d ".web" ]; then
    echo "🔧 Inicializando Reflex..."
    reflex init --loglevel warning
fi

# Start the application
echo ""
echo "✅ Iniciando aplicación..."
echo "   URL: http://localhost:3000"
echo ""
reflex run

