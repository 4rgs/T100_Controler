#!/bin/bash

# Script de actualización lite para uso en servicio systemd
# Versión silenciosa sin interacción del usuario

set -e

# Variables
PROJECT_DIR="/opt/web-control/T100_Controler"
VENV_DIR="/opt/web-control/venv"

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR"

# Verificar conexión y actualizar
if ping -c 1 github.com &> /dev/null; then
    # Fetch remoto
    git fetch origin develop 2>/dev/null || exit 0
    
    # Verificar si hay cambios
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/develop)
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        # Stash cambios locales si existen
        if ! git diff-index --quiet HEAD --; then
            git stash push -m "Auto-stash $(date)" 2>/dev/null || true
        fi
        
        # Pull cambios
        git pull origin develop 2>/dev/null || exit 0
        
        # Activar entorno virtual
        source "$VENV_DIR/bin/activate" 2>/dev/null || exit 0
        
        # Actualizar dependencias si cambió requirements.txt o por seguridad
        if git diff HEAD@{1} --name-only 2>/dev/null | grep -q requirements.txt || ! pip check 2>/dev/null; then
            pip install --upgrade pip --quiet 2>/dev/null || true
            pip install -r requirements.txt --quiet 2>/dev/null || true
        fi
    fi
fi

exit 0
