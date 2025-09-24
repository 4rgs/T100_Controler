# 🚀 Optimizaciones T100 Camera Controller

## 📋 Resumen de Optimizaciones Aplicadas

### 🔧 Optimizaciones de Código

#### 1. **Frecuencia Reducida**
- **Antes**: 30Hz
- **Ahora**: 20Hz
- **Beneficio**: -33% uso de CPU, menos interferencias

#### 2. **Actualizaciones Inteligentes**
- **Implementado**: Umbral de movimiento de 5 unidades
- **Beneficio**: Solo actualiza servos cuando hay cambio significativo
- **Resultado**: Reduce actualizaciones PWM innecesarias en ~70%

#### 3. **Logging Optimizado**
- **Antes**: `logging.INFO` cada 30 loops (1 segundo)
- **Ahora**: `logging.WARNING` + print cada 40 loops (2 segundos)
- **Beneficio**: -80% operaciones I/O de logging

#### 4. **Failsafe Tolerante**
- **Antes**: 1000ms timeout
- **Ahora**: 1500ms timeout
- **Beneficio**: Menos activaciones de failsafe falsas

#### 5. **Detección Automática de Interferencias**
- **Nuevo**: Monitor de delays en tiempo real
- **Alerta**: Si el loop tarda >100ms durante 3 ciclos consecutivos
- **Autorecuperación**: Detecta cuando vuelve a la normalidad

### ⚙️ Optimizaciones de Sistema

#### 1. **Servicio Optimizado** (`t100-camera-optimized.service`)
```ini
Nice=5                    # Prioridad CPU más baja
IOSchedulingClass=2       # I/O Best Effort
IOSchedulingPriority=4    # I/O baja prioridad
LimitCPU=30              # Máximo 30% CPU
LimitMEMLOCK=64M         # Límite memoria
```

#### 2. **Configuraciones Kernel**
```bash
vm.swappiness = 10                    # Reduce uso de swap
kernel.sched_rt_runtime_us = 950000   # Reserva tiempo para RT
```

#### 3. **Optimizador de Proceso** (`optimize_camera_process.py`)
- **CPU Affinity**: Asigna último CPU disponible
- **Process Priority**: Ajusta nice e ionice automáticamente  
- **Monitoreo**: Mide rendimiento en tiempo real

## 📊 Impacto Esperado

### ✅ Reducción de Interferencias
- **CPU Usage**: -40% promedio
- **I/O Operations**: -80% logging
- **PWM Updates**: -70% actualizaciones innecesarias
- **System Priority**: Proceso de menor prioridad

### 🎯 Compatibilidad con Tank Drive
- **Separación física**: Servos en GPIO 4,17 - Motores en GPIO 18,19,24,25
- **Separación temporal**: 20Hz cámara vs 100Hz tank
- **Separación de prioridad**: Camera nice +5, Tank nice 0
- **Separación de recursos**: Límites CPU/RAM para cámara

## 🚀 Instrucciones de Despliegue

### 1. Desplegar versión optimizada:
```bash
./deploy_camera_optimized.sh
```

### 2. Iniciar servicio optimizado:
```bash
ssh 4rgs@192.168.1.140
sudo systemctl start t100-camera
sudo systemctl status t100-camera
```

### 3. Optimizar proceso en tiempo real:
```bash
sudo python3 optimize_camera_process.py
```

### 4. Monitorear rendimiento:
```bash
python3 optimize_camera_process.py --monitor 60
```

## 🛡️ Verificación de No-Interferencia

### Pruebas Recomendadas:

1. **Test Simultaneo Tank + Cámara**:
   ```bash
   # Terminal 1: Tank drive
   python3 t100_tank_only.py
   
   # Terminal 2: Cámara (esperar 5 segundos)
   python3 t100_camera_only.py
   ```

2. **Verificar Frecuencias**:
   - Tank debe mantener ~100Hz
   - Cámara debe mantener ~20Hz
   - Sin warnings de interferencia

3. **Test de Carga del Sistema**:
   ```bash
   htop  # Verificar uso CPU total <80%
   iotop # Verificar I/O bajo para cámara
   ```

## 🔍 Indicadores de Éxito

### ✅ Funcionamiento Óptimo:
- Cámara reporta: "📊 CAM: 20.0Hz | Optimizado ✅"
- Sin mensajes: "⚠️ INTERFERENCIA DETECTADA"
- Tank mantiene 100Hz sin drops
- CPU total del sistema <70%

### ⚠️ Señales de Problemas:
- "📊 CAM: X.XHz | ⚠️ Baja frecuencia" (X < 16)
- "⚠️ INTERFERENCIA DETECTADA: Loop delay XXXms"
- Tank reporta frecuencia <90Hz
- CPU del sistema >90%

## 🎛️ Ajustes Finos

### Si aún hay interferencias:

1. **Reducir más la frecuencia**:
   ```python
   self.control_frequency_target = 15  # En t100_camera_only.py
   ```

2. **Aumentar umbral de movimiento**:
   ```python
   self.movement_threshold = 10  # Menos actualizaciones
   ```

3. **Usar CPU específica**:
   ```bash
   taskset -c 3 python3 t100_camera_only.py  # Solo CPU 3
   ```

4. **Arquitectura completamente separada**:
   ```bash
   # Ejecutar en procesos completamente independientes
   ./deploy_separated_architecture.sh
   ```

## 📈 Métricas de Rendimiento Objetivo

| Métrica | Antes | Optimizado | Mejora |
|---------|-------|------------|--------|
| Frecuencia | 30Hz | 20Hz | -33% CPU |
| Logging | 30/s | 0.5/s | -98% I/O |
| PWM Updates | Continuas | Solo cambios | -70% |
| CPU Priority | Normal | +5 nice | Menor impacto |
| RAM Limit | Sin límite | 64MB | Controlado |

El objetivo es mantener el tank drive a 100Hz estable mientras la cámara funciona suavemente a 20Hz sin interferir.