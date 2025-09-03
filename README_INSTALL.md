# T100 Motor Controller - Instalación en Raspberry Pi

## 🚀 Instalación Automática

### Opción 1: Instalación completa (recomendada)
```bash
# Descargar y ejecutar script de instalación
curl -sSL https://raw.githubusercontent.com/4rgs/T100_Controler/develop/install_rpi.sh | bash
```

### Opción 2: Instalación manual

#### 1. Clonar repositorio
```bash
cd /opt
sudo git clone -b develop https://github.com/4rgs/T100_Controler.git t100-controller
sudo chown -R 4rgs:4rgs t100-controller
cd t100-controller
```

#### 2. Configurar virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Habilitar pigpiod
```bash
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

#### 4. Instalar servicio
```bash
sudo cp t100-controller.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable t100-controller
sudo systemctl start t100-controller
```

## 🔧 Configuración

### Verificar hardware (pines por defecto):
- **Motor A (izq)**: ENA=GPIO12, IN1=GPIO16, IN2=GPIO20
- **Motor B (der)**: ENB=GPIO26, IN3=GPIO19, IN4=GPIO21

### Modificar configuración:
```bash
nano /opt/t100-controller/src/config/settings.py
```

## 📊 Monitoreo

### Ver estado del servicio:
```bash
sudo systemctl status t100-controller
```

### Ver logs en tiempo real:
```bash
sudo journalctl -u t100-controller -f
```

### Reiniciar servicio:
```bash
sudo systemctl restart t100-controller
```

## 🌐 Acceso Web

Una vez instalado, acceder a:
```
http://[IP_DE_TU_RPI]:8080
```

Para encontrar la IP:
```bash
hostname -I
```

## 🛠️ Troubleshooting

### Si el servicio no inicia:
```bash
# Ver logs de error
sudo journalctl -u t100-controller -n 20

# Verificar pigpiod
sudo systemctl status pigpiod

# Probar manualmente
cd /opt/t100-controller
source venv/bin/activate
python3 main.py
```

### Si no responde el hardware:
```bash
# Verificar permisos GPIO
sudo usermod -a -G gpio 4rgs

# Verificar pigpiod
sudo systemctl restart pigpiod
```

## 📦 Dependencias

- Python 3.7+
- pigpiod (daemon GPIO)
- Flask 3.0.3
- flask-sock 0.7.0
- pigpio 1.79
- simple-websocket 1.0.0

## 🔄 Actualización

Para actualizar a la última versión:
```bash
cd /opt/t100-controller
sudo systemctl stop t100-controller
git pull origin develop
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start t100-controller
```
