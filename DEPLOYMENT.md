# Scripts de Instalación y Actualización - T100 Controller

Este directorio contiene scripts para facilitar la instalación y actualización del T100 Controller en Raspberry Pi.

## 📋 Scripts Disponibles

### � **Auto-actualización en Servicio**

#### �🔄 `start_with_update.sh` (Nuevo - Recomendado)
Script wrapper que actualiza automáticamente antes de iniciar la aplicación.

**Características:**
- ✅ Auto-actualización en cada inicio del servicio
- � Manejo completo del entorno virtual Python
- � Instalación automática de nuevas dependencias
- � Verificación de dependencias críticas
- 💾 Backup automático de cambios locales
- 📊 Logging detallado con timestamps
- � Detección de conectividad

#### ⚙️ `t100-controller-autoupdate.service`
Servicio systemd con auto-actualización integrada.

#### 🔄 `migrate_to_autoupdate.sh`
Migra del servicio manual al servicio con auto-actualización.

**Uso:**
```bash
sudo ./migrate_to_autoupdate.sh
```

### �️ **Scripts de Mantenimiento**

#### 🔍 `verify_environment.sh`
Verifica y repara el entorno Python completo.

**Características:**
- ✅ Verifica entorno virtual
- 📚 Instala dependencias faltantes
- � Actualiza pip automáticamente
- 🧪 Test de importaciones del proyecto

**Uso:**
```bash
./verify_environment.sh
```

#### 🔄 `update_t100.sh` 
Script completo de actualización manual con verificaciones.

#### ⚡ `update_simple.sh` 
Script básico para actualizaciones rápidas manuales.

#### 🚀 `install_complete.sh`
Script de instalación completa desde cero.

## 🎯 Flujo de Trabajo Recomendado

### Primera Instalación
```bash
# 1. Clonar el repositorio
git clone https://github.com/4rgs/T100_Controler.git
cd T100_Controler

# 2. Ejecutar instalación completa
sudo ./install_complete.sh

# 3. Migrar a auto-actualización (opcional pero recomendado)
sudo ./migrate_to_autoupdate.sh
```

### Con Auto-actualización (Recomendado)
```bash
# El servicio se actualiza automáticamente en cada reinicio
sudo systemctl restart t100-controller-autoupdate.service

# Ver logs de auto-actualización
journalctl -u t100-controller-autoupdate.service -f
```

### Actualizaciones Manuales (Si no usas auto-actualización)
```bash
sudo ./update_t100.sh
```

## 📁 Estructura de Archivos en Raspberry Pi

Después de la instalación:
```
/opt/web-control/
├── T100_Controler/          # Código del proyecto
├── venv/                    # Entorno virtual Python
└── (otros archivos)

/etc/systemd/system/
└── web-motor.service        # Servicio systemd
```

## 🔧 Comandos de Servicio

```bash
# Ver estado
sudo systemctl status web-motor.service

# Iniciar servicio
sudo systemctl start web-motor.service

# Detener servicio
sudo systemctl stop web-motor.service

# Reiniciar servicio
sudo systemctl restart web-motor.service

# Ver logs en tiempo real
journalctl -u web-motor.service -f

# Ver logs de las últimas líneas
journalctl -u web-motor.service -n 50
```

## 🌐 Acceso Web

Una vez instalado y ejecutándose:
- **URL local**: http://localhost:8080
- **URL red local**: http://[IP_RASPBERRY]:8080
- **Ejemplo**: http://192.168.1.100:8080

## 🔍 Solución de Problemas

### El servicio no inicia
```bash
# Ver logs detallados
journalctl -u web-motor.service -n 100

# Verificar permisos
ls -la /opt/web-control/

# Verificar pigpiod
sudo systemctl status pigpiod
```

### Error de permisos GPIO
```bash
# Agregar usuario al grupo gpio
sudo usermod -a -G gpio 4rgs

# Reiniciar sesión o reboot
sudo reboot
```

### Error de dependencias Python
```bash
# Reinstalar entorno virtual
cd /opt/web-control
sudo rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r T100_Controler/requirements.txt
```

## 🔄 Proceso de Actualización

El script `update_t100.sh` realiza estos pasos:

1. 📁 Navega al directorio del proyecto
2. 📡 Obtiene últimos cambios de GitHub
3. 🔍 Verifica si hay actualizaciones
4. 💾 Guarda cambios locales si existen
5. 📥 Descarga nueva versión
6. 🔄 Recarga systemd daemon
7. ▶️ Reinicia el servicio
8. ✅ Verifica que funcione correctamente

## 🛡️ Seguridad

- Todos los scripts requieren permisos de root (`sudo`)
- Se verifican rutas y permisos antes de ejecutar
- Se hace backup automático de cambios locales
- Verificación de estado del servicio después de cambios

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `journalctl -u web-motor.service -f`
2. Verifica el estado: `sudo systemctl status web-motor.service`
3. Ejecuta el script de actualización: `sudo ./update_t100.sh`
