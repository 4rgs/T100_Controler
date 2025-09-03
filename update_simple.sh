#!/bin/bash

# Script simple de actualización T100 Controller
# Uso: sudo ./update_simple.sh

# Cambiar al directorio del proyecto
cd /opt/web-motor/T100_Controler

# Hacer pull de la rama develop
git pull origin develop

# Volver al directorio base
cd /opt/web-motor

# Recargar systemd y reiniciar servicio
systemctl daemon-reload
systemctl restart web-motor.service

# Mostrar estado
echo "✅ Actualización completada"
systemctl status web-motor.service --no-pager -l
