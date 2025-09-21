#!/bin/bash

# Script de instalación para T100 ZK-5AD Controller  
# Para Raspberry Pi Zero 2W con driver ZK-5AD (TA6586)

echo "🚗 Instalando T100 ZK-5AD Controller..."

# Eliminar servicios obsoletos primero
echo "🧹 Eliminando servicios T100 obsoletos..."
sudo systemctl stop t100 2>/dev/null || true
sudo systemctl stop t100-fixed 2>/dev/null || true  
sudo systemctl stop t100-elrs 2>/dev/null || true
sudo systemctl disable t100 2>/dev/null || true
sudo systemctl disable t100-fixed 2>/dev/null || true
sudo systemctl disable t100-elrs 2>/dev/null || true
sudo rm -f /etc/systemd/system/t100.service
sudo rm -f /etc/systemd/system/t100-fixed.service
sudo rm -f /etc/systemd/system/t100-elrs.service
sudo systemctl daemon-reload

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update
sudo apt upgrade -y

# Instalar dependencias del sistema
echo "🔧 Instalando dependencias del sistema..."
sudo apt install -y python3-pip python3-venv git

# Instalar pigpio
echo "📡 Instalando pigpio..."
sudo apt install -y pigpio python3-pigpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Crear entorno virtual
echo "🐍 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
echo "📚 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar GPIO automático al boot
echo "🔧 Configurando inicialización GPIO ZK-5AD..."
sudo cp zk5ad_gpio_init.py /usr/local/bin/
sudo chmod +x /usr/local/bin/zk5ad_gpio_init.py

# Crear servicio de inicialización GPIO
sudo tee /etc/systemd/system/zk5ad-gpio-init.service > /dev/null << EOF
[Unit]
Description=ZK-5AD GPIO Initialization
After=pigpiod.service
Wants=pigpiod.service

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/bin/zk5ad_gpio_init.py
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Crear script de inicio manual
echo "🚀 Creando script de inicio..."
cat > start_t100.sh << 'EOF'
#!/bin/bash
cd /home/4rgs/t100
source venv/bin/activate
python3 t100_controller.py
EOF

chmod +x start_t100.sh

# Crear servicio systemd principal
echo "⚙️ Creando servicio systemd ZK-5AD..."
sudo tee /etc/systemd/system/t100-zk5ad.service > /dev/null << EOF
[Unit]
Description=T100 ZK-5AD Tank Controller
After=network.target pigpiod.service zk5ad-gpio-init.service
Wants=pigpiod.service zk5ad-gpio-init.service

[Service]
Type=simple
User=4rgs
WorkingDirectory=/home/4rgs/t100
Environment=PATH=/home/4rgs/t100/venv/bin
ExecStart=/home/4rgs/t100/venv/bin/python /home/4rgs/t100/t100_controller.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configurar permisos GPIO para usuario 4rgs
echo "🔐 Configurando permisos GPIO..."
sudo usermod -a -G gpio 4rgs

# Habilitar servicios
echo "🎯 Habilitando servicios ZK-5AD..."
sudo systemctl enable zk5ad-gpio-init.service
sudo systemctl enable t100-zk5ad.service
sudo systemctl daemon-reload

echo ""
echo "✅ INSTALACIÓN ZK-5AD COMPLETADA!"
echo "🚀 T100 con driver ZK-5AD (TA6586) configurado"
echo ""
echo "🎮 SERVICIOS CONFIGURADOS:"
echo "  zk5ad-gpio-init.service  → Inicialización GPIO al boot"
echo "  t100-zk5ad.service       → Controlador principal"
echo ""
echo "🚀 INICIAR SISTEMA:"
echo "  sudo systemctl start zk5ad-gpio-init"
echo "  sudo systemctl start t100-zk5ad"
echo ""
echo "📋 EJECUTAR MANUALMENTE:"
echo "  ./start_t100.sh"
echo ""
echo "📊 VER LOGS:"
echo "  sudo journalctl -u t100-zk5ad -f"
echo ""
echo "🚨 PARADA DE EMERGENCIA:"
echo "  python3 emergency_stop.py"
echo ""
echo "🎯 CONFIGURACIÓN:"
echo "  Tank drive: CH2=Forward/Back, CH4=Left/Right"
echo "  GPIO ZK-5AD: 12,13,18,19 (hardware PWM)"
echo "  Freno automático: H+H al inicio y parada"
