#!/bin/bash

# Script de instalación para T100 Controller
# Para Raspberry Pi Zero 2W

echo "🚗 Instalando T100 Controller..."

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

# Crear script de inicio
echo "🚀 Creando script de inicio..."
cat > start_t100.sh << 'EOF'
#!/bin/bash
cd /home/4rgs/t100
source venv/bin/activate
python3 server.py
EOF

chmod +x start_t100.sh

# Crear servicio systemd
echo "⚙️ Creando servicio systemd..."
sudo tee /etc/systemd/system/t100.service > /dev/null << EOF
[Unit]
Description=T100 Controller WebSocket Server
After=network.target pigpiod.service
Wants=pigpiod.service

[Service]
Type=simple
User=4rgs
WorkingDirectory=/home/4rgs/t100
Environment=PATH=/home/4rgs/t100/venv/bin
ExecStart=/home/4rgs/t100/venv/bin/python /home/4rgs/t100/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configurar permisos GPIO para usuario 4rgs
echo "🔐 Configurando permisos GPIO..."
sudo usermod -a -G gpio 4rgs

echo "✅ Instalación completada!"
echo ""
echo "Para iniciar el servicio:"
echo "  sudo systemctl enable t100"
echo "  sudo systemctl start t100"
echo ""
echo "Para ver logs:"
echo "  sudo journalctl -u t100 -f"
echo ""
echo "Para ejecutar manualmente:"
echo "  ./start_t100.sh"
echo ""
echo "Cliente web disponible en: client.html"
echo "Servidor corriendo en puerto: 8080"
