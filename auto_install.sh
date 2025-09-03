#!/bin/bash

# Script de auto-instalación para el sistema T100 optimizado
# Este script configura e inicia automáticamente el sistema de control

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Verificar si se ejecuta como usuario correcto
if [ "$EUID" -eq 0 ]; then
    log_error "No ejecutar este script como root. Usar usuario 'pi' o similar."
    exit 1
fi

# Banner
echo -e "${BLUE}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                    T100 CONTROL OPTIMIZADO                  ║
║                  Auto-instalación del sistema               ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar directorio actual
CURRENT_DIR=$(pwd)
if [[ ! "$CURRENT_DIR" == *"T100"* ]] && [[ ! -f "motor_control_optimized.py" ]]; then
    log_warning "No estás en el directorio correcto del proyecto T100"
    read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Paso 1: Verificar y instalar dependencias del sistema
log_step "1/6 Verificando dependencias del sistema..."

# Verificar git
if ! command -v git &> /dev/null; then
    log_error "Git no está instalado. Instalarlo primero: sudo apt install git"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 no está instalado. Instalarlo primero: sudo apt install python3 python3-pip"
    exit 1
fi

# Verificar pigpio
if ! command -v pigpiod &> /dev/null; then
    log_warning "pigpiod no encontrado, instalando..."
    sudo apt update
    sudo apt install -y pigpio python3-pigpio
fi

log_info "Dependencias del sistema verificadas ✓"

# Paso 2: Instalar dependencias de Python
log_step "2/6 Instalando dependencias de Python..."

if [ -f "requirements_optimized.txt" ]; then
    pip3 install -r requirements_optimized.txt --user --no-cache-dir
    log_info "Dependencias de Python instaladas ✓"
else
    log_warning "requirements_optimized.txt no encontrado, instalando dependencias básicas..."
    pip3 install Flask==3.0.3 flask-sock==0.7.0 pigpio==1.79 --user --no-cache-dir
fi

# Paso 3: Optimizar el sistema
log_step "3/6 Optimizando configuración del sistema..."

if [ -f "optimize_system.sh" ]; then
    chmod +x optimize_system.sh
    ./optimize_system.sh
    log_info "Sistema optimizado ✓"
else
    log_warning "Script de optimización no encontrado, configurando manualmente..."
    
    # Configuración básica de systemd
    sudo tee /etc/systemd/system/t100-control.service > /dev/null << EOF
[Unit]
Description=T100 Motor Control System
After=network.target pigpiod.service
Wants=network.target
Requires=pigpiod.service

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$(pwd)
Environment=PYTHONPATH=$(pwd)
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 motor_control_optimized.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Límites de recursos
MemoryLimit=256M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

    # Servicio pigpiod
    sudo tee /etc/systemd/system/pigpiod.service > /dev/null << EOF
[Unit]
Description=Pigpio daemon
After=network.target

[Service]
Type=forking
User=root
ExecStart=/usr/bin/pigpiod
ExecStop=/bin/systemctl kill pigpiod
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
fi

# Paso 4: Configurar inicio automático
log_step "4/6 Configurando inicio automático..."

# Habilitar servicios
sudo systemctl enable pigpiod
sudo systemctl enable t100-control 2>/dev/null || sudo systemctl enable motor-control-optimized 2>/dev/null || true

# Crear script de inicio rápido si no existe
if [ ! -f "start_optimized.sh" ]; then
    cat > start_optimized.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Iniciando T100 Control..."

# Verificar pigpiod
if ! pgrep pigpiod > /dev/null; then
    echo "Iniciando pigpiod..."
    sudo pigpiod
    sleep 2
fi

# Iniciar aplicación
python3 motor_control_optimized.py
EOF
    chmod +x start_optimized.sh
fi

log_info "Servicios configurados para inicio automático ✓"

# Paso 5: Crear enlaces y accesos directos
log_step "5/6 Creando accesos directos..."

# Crear enlace en el home del usuario
ln -sf "$(pwd)/start_optimized.sh" "$HOME/start_t100.sh" 2>/dev/null || true

# Crear script de estado del sistema
cat > check_system.sh << 'EOF'
#!/bin/bash
echo "📊 Estado del Sistema T100"
echo "=========================="

# Estado de servicios
echo "🔧 Servicios:"
systemctl is-active pigpiod 2>/dev/null && echo "  ✓ pigpiod: activo" || echo "  ✗ pigpiod: inactivo"
systemctl is-active t100-control 2>/dev/null && echo "  ✓ t100-control: activo" || echo "  ✗ t100-control: inactivo"
systemctl is-active motor-control-optimized 2>/dev/null && echo "  ✓ motor-control-optimized: activo" || echo "  ✗ motor-control-optimized: inactivo"

# Recursos del sistema
echo ""
echo "💾 Recursos:"
if command -v free &> /dev/null; then
    MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    echo "  RAM: ${MEM_USAGE}%"
fi

if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
    TEMP_C=$(echo "scale=1; $TEMP/1000" | bc 2>/dev/null || echo "N/A")
    echo "  Temperatura: ${TEMP_C}°C"
fi

# Verificar puerto
echo ""
echo "🌐 Red:"
if command -v netstat &> /dev/null; then
    if netstat -ln | grep -q ":5000"; then
        echo "  ✓ Puerto 5000: abierto"
        IP=$(hostname -I | awk '{print $1}')
        echo "  📱 URL: http://${IP}:5000"
    else
        echo "  ✗ Puerto 5000: cerrado"
    fi
fi

echo ""
echo "🔧 Comandos útiles:"
echo "  Iniciar manualmente: ./start_optimized.sh"
echo "  Ver logs: journalctl -u t100-control -f"
echo "  Reiniciar servicio: sudo systemctl restart t100-control"
EOF

chmod +x check_system.sh
log_info "Accesos directos creados ✓"

# Paso 6: Verificar instalación
log_step "6/6 Verificando instalación..."

# Verificar archivos principales
REQUIRED_FILES=("motor_control_optimized.py" "src/config/settings.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_info "  ✓ $file encontrado"
    else
        log_warning "  ✗ $file no encontrado"
    fi
done

# Verificar estructura de directorios
REQUIRED_DIRS=("src/web" "src/control" "src/hardware" "src/templates")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        log_info "  ✓ Directorio $dir existe"
    else
        log_warning "  ✗ Directorio $dir no existe"
    fi
done

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ INSTALACIÓN COMPLETADA                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "🚀 Sistema T100 Control Optimizado instalado correctamente"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Reiniciar el sistema: sudo reboot"
echo "   2. El sistema se iniciará automáticamente"
echo "   3. Acceder desde navegador: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Verificar estado: ./check_system.sh"
echo "   • Iniciar manualmente: ./start_optimized.sh"
echo "   • Ver logs: journalctl -u t100-control -f"
echo "   • Parar servicio: sudo systemctl stop t100-control"
echo ""
echo "📱 La interfaz web incluye monitor de recursos en tiempo real"
echo ""

# Preguntar si iniciar ahora
read -p "¿Iniciar el sistema ahora? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Iniciando sistema..."
    sudo systemctl start pigpiod
    sleep 2
    sudo systemctl start t100-control 2>/dev/null || sudo systemctl start motor-control-optimized 2>/dev/null || ./start_optimized.sh
fi

echo ""
log_info "🎉 ¡Instalación completada exitosamente!"
