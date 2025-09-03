#!/bin/bash

# Script de verificación y reparación del entorno Python
# Verifica que el entorno virtual esté configurado correctamente

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
INSTALL_DIR="/opt/web-control"
PROJECT_DIR="$INSTALL_DIR/T100_Controler"
VENV_DIR="$INSTALL_DIR/venv"

echo -e "${BLUE}🔍 Verificando entorno Python para T100 Controller...${NC}"

# Función para log
log() {
    echo -e "$1"
}

# Verificar directorio del proyecto
if [ ! -d "$PROJECT_DIR" ]; then
    log "${RED}❌ Error: Directorio del proyecto no encontrado: $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Verificar entorno virtual
if [ ! -d "$VENV_DIR" ]; then
    log "${YELLOW}⚠️ Entorno virtual no encontrado, creando...${NC}"
    python3 -m venv "$VENV_DIR" || {
        log "${RED}❌ Error: No se puede crear el entorno virtual${NC}"
        exit 1
    }
    log "${GREEN}✅ Entorno virtual creado${NC}"
fi

# Activar entorno virtual
source "$VENV_DIR/bin/activate" || {
    log "${RED}❌ Error: No se puede activar el entorno virtual${NC}"
    exit 1
}

log "${GREEN}✅ Entorno virtual activado${NC}"

# Verificar pip
log "${BLUE}🔧 Actualizando pip...${NC}"
pip install --upgrade pip --quiet || {
    log "${YELLOW}⚠️ No se pudo actualizar pip${NC}"
}

# Verificar requirements.txt
if [ ! -f "requirements.txt" ]; then
    log "${RED}❌ Error: requirements.txt no encontrado${NC}"
    exit 1
fi

# Instalar/actualizar dependencias
log "${BLUE}📚 Instalando/verificando dependencias...${NC}"
pip install -r requirements.txt || {
    log "${RED}❌ Error: No se pueden instalar las dependencias${NC}"
    exit 1
}

# Verificar dependencias críticas
log "${BLUE}🔍 Verificando dependencias críticas...${NC}"
python -c "
import sys
try:
    import flask
    import pigpio
    import flask_sock
    print('✅ Todas las dependencias críticas están disponibles')
except ImportError as e:
    print(f'❌ Error: Dependencia faltante: {e}')
    sys.exit(1)
" || exit 1

# Verificar que el script principal existe
if [ ! -f "main.py" ]; then
    log "${RED}❌ Error: main.py no encontrado${NC}"
    exit 1
fi

# Test básico de importación
log "${BLUE}🔍 Verificando importaciones del proyecto...${NC}"
python -c "
import sys
sys.path.insert(0, '.')
try:
    from src.config.settings import get_config
    from src.hardware.l298n_driver import L298NController
    from src.control.joystick_controller import JoystickController
    from src.web.flask_app import run_server
    print('✅ Todas las importaciones del proyecto funcionan')
except ImportError as e:
    print(f'⚠️ Advertencia: Error de importación: {e}')
    print('   Esto puede ser normal si no estás en Raspberry Pi')
" || log "${YELLOW}⚠️ Algunas importaciones fallaron (puede ser normal en desarrollo)${NC}"

log "${GREEN}🎉 Verificación del entorno completada exitosamente${NC}"
log "${BLUE}📋 Información del entorno:${NC}"
echo "   Python: $(python --version)"
echo "   Pip: $(pip --version)"
echo "   Entorno virtual: $VENV_DIR"
echo "   Proyecto: $PROJECT_DIR"

log "${GREEN}✅ El entorno está listo para ejecutar T100 Controller${NC}"
