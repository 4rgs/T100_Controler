# T100 Web Client - PWA

Cliente web profesional para control remoto del robot T100 implementado como Progressive Web App (PWA).

## 🚀 Características

### 📱 Progressive Web App
- **Instalación nativa**: Se instala como app en dispositivos móviles y de escritorio
- **Funcionamiento offline**: Interfaz de respaldo cuando no hay conexión
- **Actualizaciones automáticas**: Se actualiza automáticamente sin intervención
- **Caché inteligente**: Mejor rendimiento y menor uso de datos

### 🎮 Interfaz de Control
- **Joystick táctil**: Control preciso de movimiento
- **Estadísticas en tiempo real**: Métricas de velocidad, latencia y motores
- **Panel profesional**: Diseño serio con colores corporativos
- **Responsive design**: Adaptable a móviles y tablets

### 🔧 Funcionalidades
- **Conexión WebSocket**: Comunicación en tiempo real con el robot
- **Medición de latencia**: Monitoreo de la calidad de conexión
- **Controles de emergencia**: Parada inmediata y calibración
- **Estado del sistema**: Información detallada del robot

## 📦 Archivos

- `client.html` - Aplicación web principal con PWA
- `manifest.json` - Configuración PWA (iconos, metadata)
- `sw.js` - Service Worker para caché y offline
- `docker-compose.yml` - Despliegue en contenedores
- `casaos-app.json` - Configuración para CasaOS

## 🚀 Despliegue

### Usando Docker Compose (Recomendado)
```bash
cd web-client
docker-compose up -d
```
Acceder en: `http://localhost:8084`

### CasaOS
1. Importar `docker-compose.yml` en CasaOS
2. O usar la configuración en `casaos-app.json`

### Servidor Web Simple
Servir los archivos con cualquier servidor web HTTP:
```bash
# Python
python -m http.server 8080

# Node.js
npx serve .

# Apache/Nginx
# Copiar archivos al directorio web
```

## 📱 Instalación como PWA

1. **Navegador móvil**: Abrir en Chrome/Safari → "Agregar a pantalla de inicio"
2. **Navegador de escritorio**: Buscar icono de instalación en la barra de direcciones
3. **Automático**: La app mostrará un botón "📱 Instalar App" cuando sea posible

## 🎯 Uso

1. **Conectar**: Ingresar IP y puerto del robot T100
2. **Controlar**: Usar el joystick para movimiento
3. **Monitorear**: Ver estadísticas en tiempo real
4. **Offline**: La interfaz sigue funcionando sin conexión

## ⚙️ Configuración

### Variables de Conexión
- **IP por defecto**: `192.168.1.140`
- **Puerto por defecto**: `8080`
- **Protocolo**: WebSocket (`ws://`)

### Docker
- **Puerto del contenedor**: `8084`
- **Imagen base**: `httpd:alpine`
- **Descarga automática**: Desde GitHub

## 🔧 Desarrollo

La PWA se actualiza automáticamente desde GitHub. Para desarrollo local:

1. Editar archivos en esta carpeta
2. Servir con servidor web local
3. Los cambios se reflejan inmediatamente

## 📊 Monitoreo

La app incluye métricas avanzadas:
- Latencia de conexión
- Comandos enviados
- Velocidades de motores
- Posición del joystick
- Estado de conexión

## 🌐 Compatibilidad

- **Navegadores**: Chrome, Safari, Firefox, Edge
- **Móviles**: iOS 11.3+, Android 5.0+
- **Desktop**: Windows, macOS, Linux
- **PWA**: Instalable en todos los dispositivos modernos
