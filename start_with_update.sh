#!/bin/bash

# Script wrapper para T100 Controller
# Actualiza el código automáticamente antes de ejecutar el programa

set -e

# Variables de configuración
INSTALL_DIR="/opt/web-motor"
PROJECT_DIR="$INSTALL_DIR/T100_Controler"
PYTHON_VENV="$INSTALL_DIR/venv/bin/python"
UPDATE_SCRIPT="$PROJECT_DIR/update_t100_lite.sh"

# Colores para logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Iniciando T100 Controller con auto-actualización...${NC}"

# Función para log con timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR" || {
    log "${RED}❌ Error: No se puede acceder al directorio $PROJECT_DIR${NC}"
    exit 1
}

# Verificar si hay conexión a internet antes de intentar actualizar
if ping -c 1 github.com &> /dev/null; then
    log "${YELLOW}📡 Verificando actualizaciones...${NC}"
    
    # Intentar actualización silenciosa
    if git fetch origin develop 2>/dev/null; then
        LOCAL=$(git rev-parse HEAD)
        REMOTE=$(git rev-parse origin/develop)
        
        if [ "$LOCAL" != "$REMOTE" ]; then
            log "${YELLOW}📥 Nueva versión disponible, actualizando...${NC}"
            
            # Guardar cambios locales si existen
            if ! git diff-index --quiet HEAD --; then
                log "${YELLOW}💾 Guardando cambios locales...${NC}"
                git stash push -m "Auto-stash before service start $(date)" 2>/dev/null || true
            fi
            
            # Actualizar código
            if git pull origin develop 2>/dev/null; then
                log "${GREEN}✅ Código actualizado exitosamente${NC}"
                
                # Activar entorno virtual
                log "${BLUE}🐍 Activando entorno virtual...${NC}"
                source "$INSTALL_DIR/venv/bin/activate" || {
                    log "${RED}❌ Error: No se puede activar el entorno virtual${NC}"
                    exit 1
                }
                
                # Verificar si requirements.txt cambió en la actualización
                if git diff HEAD@{1} --name-only 2>/dev/null | grep -q requirements.txt; then
                    log "${YELLOW}📚 Detectados cambios en requirements.txt, actualizando dependencias...${NC}"
                    pip install --upgrade pip --quiet 2>/dev/null || true
                    pip install -r requirements.txt --quiet || {
                        log "${RED}⚠️ Error instalando dependencias, continuando...${NC}"
                    }
                    log "${GREEN}✅ Dependencias actualizadas${NC}"
                else
                    log "${BLUE}ℹ️ Sin cambios en dependencias${NC}"
                fi
                
                # Verificar que todas las dependencias estén instaladas
                log "${BLUE}🔍 Verificando dependencias existentes...${NC}"
                if ! pip check 2>/dev/null; then
                    log "${YELLOW}⚠️ Instalando dependencias faltantes...${NC}"
                    pip install -r requirements.txt --quiet || true
                fi
                
            else
                log "${RED}⚠️ Error en actualización, continuando con versión actual${NC}"
            fi
        else
            log "${GREEN}✅ Código ya está actualizado${NC}"
        fi
    else
        log "${YELLOW}⚠️ No se pudo verificar actualizaciones, continuando...${NC}"
    fi
else
    log "${YELLOW}⚠️ Sin conexión a internet, usando versión local${NC}"
fi

# Mostrar información de la versión actual
CURRENT_COMMIT=$(git rev-parse --short HEAD)
COMMIT_DATE=$(git show -s --format=%ci HEAD)
log "${BLUE}📋 Ejecutando versión: $CURRENT_COMMIT ($COMMIT_DATE)${NC}"

# Verificar que el entorno virtual existe
if [ ! -f "$PYTHON_VENV" ]; then
    log "${RED}❌ Error: No se encuentra el entorno virtual en $PYTHON_VENV${NC}"
    exit 1
fi

# Activar entorno virtual antes de ejecutar (asegurar que esté activo)
log "${BLUE}🐍 Activando entorno virtual para ejecución...${NC}"
source "$INSTALL_DIR/venv/bin/activate" || {
    log "${RED}❌ Error: No se puede activar el entorno virtual${NC}"
    exit 1
}

# Verificar que las dependencias principales estén disponibles
log "${BLUE}🔍 Verificando dependencias críticas...${NC}"
python -c "import flask, pigpio, flask_sock" 2>/dev/null || {
    log "${YELLOW}⚠️ Instalando dependencias faltantes...${NC}"
    pip install -r requirements.txt --quiet || {
        log "${RED}❌ Error: No se pueden instalar las dependencias${NC}"
        exit 1
    }
}

# Ejecutar el programa principal
log "${GREEN}▶️ Iniciando aplicación Python...${NC}"
exec "$PYTHON_VENV" main.py
