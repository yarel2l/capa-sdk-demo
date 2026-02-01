#!/bin/bash

# Script de verificación del proyecto CAPA Demo

echo "🔍 Verificación del Proyecto CAPA Demo"
echo "======================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de checks
PASSED=0
FAILED=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2 (falta: $1)"
        ((FAILED++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2 (falta: $1)"
        ((FAILED++))
    fi
}

echo "📁 Verificando estructura de directorios..."
check_dir "demo_reflex" "Directorio principal"
check_dir "demo_reflex/demo_reflex" "Directorio de código fuente"
check_dir "demo_reflex/assets" "Directorio de assets"
check_dir "demo_reflex/.web" "Directorio web (generado)"
echo ""

echo "📄 Verificando archivos de código..."
check_file "demo_reflex/demo_reflex/__init__.py" "Paquete Python"
check_file "demo_reflex/demo_reflex/demo_reflex.py" "App principal"
check_file "demo_reflex/demo_reflex/state.py" "Estados de Reflex"
check_file "demo_reflex/demo_reflex/pages.py" "Páginas"
check_file "demo_reflex/demo_reflex/components.py" "Componentes"
check_file "demo_reflex/demo_reflex/capa_service.py" "Servicio CAPA"
echo ""

echo "📚 Verificando documentación..."
check_file "demo_reflex/README.md" "README principal"
check_file "demo_reflex/QUICKSTART.md" "Guía rápida"
check_file "demo_reflex/GUIA_USO.md" "Guía de uso"
check_file "demo_reflex/DESARROLLO.md" "Guía de desarrollo"
check_file "demo_reflex/RESUMEN.md" "Resumen ejecutivo"
check_file "demo_reflex/DOC_INDEX.md" "Índice de documentación"
echo ""

echo "⚙️ Verificando archivos de configuración..."
check_file "demo_reflex/requirements.txt" "Dependencias"
check_file "demo_reflex/rxconfig.py" "Configuración Reflex"
check_file "demo_reflex/.gitignore" "Gitignore"
check_file "demo_reflex/start.sh" "Script de inicio"
echo ""

echo "🔧 Verificando permisos..."
if [ -x "demo_reflex/start.sh" ]; then
    echo -e "${GREEN}✓${NC} start.sh es ejecutable"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} start.sh no es ejecutable"
    ((FAILED++))
fi
echo ""

echo "📦 Verificando instalación de Python..."
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python3 instalado"
    ((PASSED++))
    PYTHON_VERSION=$(python3 --version)
    echo "  $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python3 no encontrado"
    ((FAILED++))
fi
echo ""

echo "🐍 Verificando entorno virtual..."
if [ -d "../.venv" ]; then
    echo -e "${GREEN}✓${NC} Entorno virtual del proyecto padre existe"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Entorno virtual no encontrado en directorio padre"
fi
echo ""

echo "📊 Verificando módulo CAPA..."
if python3 -c "import sys; sys.path.insert(0, '..'); import capa" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Módulo CAPA importable"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Módulo CAPA no se puede importar"
    ((FAILED++))
    echo "  Ejecuta: cd .. && pip install -e ."
fi
echo ""

echo "🌐 Verificando Reflex..."
if python3 -c "import reflex" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Reflex instalado"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Reflex no instalado"
    ((FAILED++))
    echo "  Ejecuta: pip install reflex"
fi
echo ""

# Resumen
echo "======================================"
echo "📊 RESUMEN"
echo "======================================"
echo -e "Tests pasados: ${GREEN}$PASSED${NC}"
echo -e "Tests fallidos: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ¡Proyecto verificado exitosamente!${NC}"
    echo ""
    echo "🚀 Puedes iniciar la aplicación con:"
    echo "   cd demo_reflex && ./start.sh"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Hay algunos problemas que resolver${NC}"
    echo ""
    echo "💡 Sugerencias:"
    echo "   1. Revisa los archivos faltantes"
    echo "   2. Verifica la instalación de dependencias"
    echo "   3. Consulta la documentación en DOC_INDEX.md"
    echo ""
    exit 1
fi
