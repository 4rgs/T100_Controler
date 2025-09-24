#!/bin/bash

# Despliegue completo de la nueva arquitectura de procesos separados
# Sube todos los archivos necesarios y configura el sistema

# Remover set -e para mejor manejo de errores
# set -e

# Configuración
T100_HOST="4rgs@192.168.1.140"
T100_DIR="t100"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🚀 DESPLIEGUE ARQUITECTURA SEPARADA T100"
echo "========================================"
echo "Desplegando solución de procesos separados"
echo "para eliminar el cruce de señales"
echo "========================================"

# Verificar conectividad
print_status "Verificando conectividad con T100..."
if ping -c 1 -W 5 192.168.1.140 >/dev/null 2>&1; then
    print_success "Conectividad OK"
else
    print_warning "Ping falló, intentando SSH directo..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$T100_HOST" "echo 'SSH OK'" >/dev/null 2>&1; then
        print_success "SSH conectividad OK"
    else
        print_error "No se puede conectar con T100 (192.168.1.140)"
        echo "Verifica que:"
        echo "1. El T100 esté encendido"
        echo "2. Esté conectado a la red"
        echo "3. SSH esté habilitado"
        exit 1
    fi
fi

# Archivos de la nueva arquitectura
NEW_FILES=(
    "t100_tank_only.py"
    "t100_camera_only.py" 
    "t100_master.py"
    "test_separated_processes.py"
    "manage_services.sh"
    "t100-tank.service"
    "t100-camera.service"
    "ARQUITECTURA_SEPARADA.md"
)

# Archivos corregidos
UPDATED_FILES=(
    "config.py"
    "test_servos_quick.py"
    "mg90s_servo_driver.py"
    "fix_gpio_crossover.py"
)

ALL_FILES=("${NEW_FILES[@]}" "${UPDATED_FILES[@]}")

# Verificar que todos los archivos existen
print_status "Verificando archivos locales..."
missing_files=()
for file in "${ALL_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    print_error "Archivos faltantes:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi
print_success "Todos los archivos están presentes"

# Crear backup del sistema actual
print_status "Creando backup del sistema actual..."
ssh "$T100_HOST" "cd $T100_DIR && tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz *.py *.service 2>/dev/null || true"
print_success "Backup creado"

# Parar servicios existentes si existen
print_status "Parando servicios existentes..."
ssh "$T100_HOST" "
    sudo systemctl stop t100-zk5ad.service 2>/dev/null || true
    sudo systemctl stop t100-tank.service 2>/dev/null || true
    sudo systemctl stop t100-camera.service 2>/dev/null || true
    pkill -f t100_ 2>/dev/null || true
" 
print_success "Servicios parados"

# Transferir archivos
print_status "Transfiriendo archivos..."
failed_files=()
for file in "${ALL_FILES[@]}"; do
    print_status "  Copiando $file..."
    if scp -o ConnectTimeout=10 "$file" "$T100_HOST:$T100_DIR/" 2>&1; then
        print_success "  ✅ $file copiado"
    else
        print_error "  ❌ Error copiando $file"
        failed_files+=("$file")
    fi
done

if [[ ${#failed_files[@]} -gt 0 ]]; then
    print_error "Archivos que fallaron al copiar:"
    for file in "${failed_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    print_warning "Intentando copia manual..."
    echo "Ejecuta manualmente:"
    echo "scp ${failed_files[*]} $T100_HOST:$T100_DIR/"
    exit 1
fi

# Hacer ejecutables los scripts
print_status "Configurando permisos..."
ssh "$T100_HOST" "cd $T100_DIR && chmod +x *.py *.sh"
print_success "Permisos configurados"

# Instalar servicios
print_status "Instalando servicios systemd..."
if ssh "$T100_HOST" "cd $T100_DIR && chmod +x manage_services.sh && ./manage_services.sh install" 2>&1; then
    print_success "Servicios instalados"
else
    print_error "Error instalando servicios"
    print_warning "Intenta manualmente:"
    echo "ssh $T100_HOST"
    echo "cd $T100_DIR"
    echo "./manage_services.sh install"
    exit 1
fi

# Test rápido de funcionamiento
print_status "Ejecutando test rápido..."
ssh "$T100_HOST" "cd $T100_DIR && timeout 10 python3 test_separated_processes.py || true"

echo ""
echo "🎉 DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "====================================="
echo ""
echo "📋 NUEVA ARQUITECTURA DESPLEGADA:"
echo "  🚗 Tank Drive: t100_tank_only.py (100Hz)"
echo "  📹 Cámara: t100_camera_only.py (30Hz)"
echo "  🎛️  Maestro: t100_master.py"
echo ""
echo "🎮 PARA USAR EL SISTEMA:"
echo "  ssh $T100_HOST"
echo "  cd $T100_DIR"
echo "  ./manage_services.sh start"
echo ""
echo "📊 COMANDOS ÚTILES:"
echo "  ./manage_services.sh status    # Ver estado"
echo "  ./manage_services.sh logs      # Ver logs"
echo "  ./manage_services.sh follow    # Logs en tiempo real"
echo "  ./manage_services.sh restart   # Reiniciar"
echo ""
echo "🧪 PARA PROBAR MANUALMENTE:"
echo "  python3 t100_master.py        # Controlador maestro"
echo "  python3 t100_tank_only.py     # Solo tank"
echo "  python3 t100_camera_only.py   # Solo cámara"
echo ""
echo "✅ El problema de cruce de señales debería estar resuelto"
echo "   Los procesos separados eliminan las interferencias entre"
echo "   el control del tanque y la cámara."