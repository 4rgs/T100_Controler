/* ====== Canvas joystick (virtual) ====== */
const pad = document.getElementById('pad');
const ctx = pad.getContext('2d');
const R = 120, KNOB = 22;
let stick = {x:0, y:0}, dragging=false;

function draw(){
    ctx.clearRect(0,0,pad.width,pad.height);
    const cx=pad.width/2, cy=pad.height/2;
    ctx.beginPath(); ctx.arc(cx,cy,R+10,0,Math.PI*2); ctx.strokeStyle='#232334'; ctx.lineWidth=8; ctx.stroke();
    ctx.strokeStyle='#2f2f42'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(cx-R-6,cy); ctx.lineTo(cx+R+6,cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx,cy-R-6); ctx.lineTo(cx,cy+R+6); ctx.stroke();
    const kx=cx+stick.x*R, ky=cy-stick.y*R;
    ctx.beginPath(); ctx.arc(kx,ky,KNOB,0,Math.PI*2); ctx.fillStyle='#2b2b3d'; ctx.strokeStyle='#3a3a56'; ctx.lineWidth=2; ctx.fill(); ctx.stroke();
}

function setStickFromEvent(e){
    const rect=pad.getBoundingClientRect(), cx=rect.left+pad.width/2, cy=rect.top+pad.height/2;
    let px,py; 
    if(e.touches&&e.touches.length){
        px=e.touches[0].clientX;
        py=e.touches[0].clientY;
    } else {
        px=e.clientX;
        py=e.clientY;
    }
    let dx=px-cx, dy=py-cy; 
    const mag=Math.hypot(dx,dy), max=R; 
    if(mag>max){
        dx=dx*max/mag; 
        dy=dy*max/mag;
    }
    stick.x=+(dx/R).toFixed(3);
    stick.y=+(-dy/R).toFixed(3);  // ↑ positivo (NO invertido)
    draw(); 
    sendXY(stick.x, stick.y);
}

function centerStick(){ 
    stick.x=0; 
    stick.y=0; 
    draw(); 
    sendXY(0,0); 
}

/* ====== WebSocket Ultra-Optimizado con AbortController ====== */
let ws = null;
let wsOpen = false;
let last = {x: 0, y: 0};
let commandQueue = [];
let currentController = null;
let lastSendTime = 0;
let reconnectAttempts = 0;
const maxReconnectAttempts = 10;

// Configuración de latencia ultra-baja
const LATENCY_CONFIG = {
    maxDelay: 100,           // Máximo delay permitido (100ms)
    batchInterval: 8,        // Enviar cada 8ms (125 FPS)
    abortTimeout: 50,        // Abortar comandos > 50ms
    priorityThreshold: 0.01  // Cambios mínimos para enviar
};

// Queue de comandos con timestamp
class CommandQueue {
    constructor() {
        this.queue = [];
        this.processing = false;
    }
    
    add(command) {
        const now = performance.now();
        command.timestamp = now;
        
        // Abortar comandos antiguos
        this.abortOldCommands(now);
        
        // Solo agregar si el cambio es significativo
        if (this.isSignificantChange(command)) {
            this.queue.push(command);
            this.processQueue();
        }
    }
    
    abortOldCommands(currentTime) {
        this.queue = this.queue.filter(cmd => {
            const age = currentTime - cmd.timestamp;
            return age < LATENCY_CONFIG.abortTimeout;
        });
    }
    
    isSignificantChange(command) {
        if (this.queue.length === 0) return true;
        const lastCmd = this.queue[this.queue.length - 1];
        const deltaX = Math.abs(command.x - lastCmd.x);
        const deltaY = Math.abs(command.y - lastCmd.y);
        return deltaX > LATENCY_CONFIG.priorityThreshold || 
               deltaY > LATENCY_CONFIG.priorityThreshold;
    }
    
    processQueue() {
        if (this.processing || this.queue.length === 0 || !wsOpen) return;
        
        this.processing = true;
        const command = this.queue.shift();
        
        // Verificar si el comando sigue siendo válido
        const age = performance.now() - command.timestamp;
        if (age > LATENCY_CONFIG.maxDelay) {
            this.processing = false;
            this.processQueue(); // Procesar siguiente
            return;
        }
        
        this.sendCommand(command);
    }
    
    sendCommand(command) {
        if (!ws || !wsOpen) {
            this.processing = false;
            return;
        }
        
        try {
            const payload = JSON.stringify({
                x: command.x,
                y: command.y,
                timestamp: command.timestamp,
                priority: 'high'
            });
            
            ws.send(payload);
            last.x = command.x;
            last.y = command.y;
            lastSendTime = performance.now();
            
        } catch (error) {
            console.error('❌ Error enviando comando:', error);
        }
        
        this.processing = false;
        
        // Procesar siguiente comando inmediatamente si existe
        if (this.queue.length > 0) {
            setTimeout(() => this.processQueue(), 1);
        }
    }
}

const cmdQueue = new CommandQueue();
const baseReconnectDelay = 500;

// WebSocket ultra-optimizado
function connectWS(){
    if(ws && ws.readyState === WebSocket.CONNECTING) return;
    
    try {
        const proto = location.protocol === 'https:' ? 'wss' : 'ws';
        ws = new WebSocket(`${proto}://${location.host}/ws/joystick`);
        
        // Configuración de buffer ultra-baja latencia
        ws.binaryType = 'arraybuffer';
        
        document.getElementById('wsstat').textContent = 'ws: conectando…';
        document.getElementById('wsstat').className = 'pill warning';
        
        ws.onopen = () => {
            wsOpen = true; 
            reconnectAttempts = 0;
            document.getElementById('wsstat').textContent = 'ws: conectado'; 
            document.getElementById('wsstat').className = 'pill ok';
            
            console.log('� WebSocket conectado con latencia ultra-baja');
            
            // Enviar configuración de latencia
            ws.send(JSON.stringify({
                type: 'config',
                latencyMode: 'ultra-low',
                batchInterval: LATENCY_CONFIG.batchInterval
            }));
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                // Medir latencia real
                if (data.timestamp) {
                    const latency = performance.now() - data.timestamp;
                    updateLatencyDisplay(latency);
                }
                
                // Actualizar estado de motores si está disponible
                if (data.A && data.B) {
                    updateMotorStatus(data.A, data.B);
                }
                
            } catch (e) {
                console.warn('⚠️ Error procesando respuesta:', e);
            }
        };
        
        ws.onclose = (event) => {
            wsOpen = false; 
            console.log(`🔌 WebSocket cerrado: ${event.code}`);
            
            document.getElementById('wsstat').textContent = 'ws: reconectando…'; 
            document.getElementById('wsstat').className = 'pill bad';
            
            // Reconexión exponencial con límite
            if (reconnectAttempts < maxReconnectAttempts) {
                const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
                reconnectAttempts++;
                console.log(`🔄 Reconectando en ${delay}ms (intento ${reconnectAttempts})`);
                setTimeout(connectWS, delay);
            } else {
                document.getElementById('wsstat').textContent = 'ws: error permanente'; 
                document.getElementById('wsstat').className = 'pill bad';
            }
        };
        
        ws.onerror = (error) => {
            console.error('❌ Error WebSocket:', error);
        };
        
    } catch (error) {
        console.error('❌ Error creando WebSocket:', error);
    }
}

// Función optimizada para envío ultra-rápido
function sendXY(x, y) {
    // Aplicar deadzone en cliente para reducir tráfico
    const deadzone = 0.02;
    if (Math.abs(x) < deadzone) x = 0;
    if (Math.abs(y) < deadzone) y = 0;
    
    // Solo enviar si hay cambio significativo
    const deltaX = Math.abs(x - last.x);
    const deltaY = Math.abs(y - last.y);
    
    if (deltaX < LATENCY_CONFIG.priorityThreshold && 
        deltaY < LATENCY_CONFIG.priorityThreshold) {
        return; // Sin cambios significativos
    }
    
    // Agregar a queue con prioridad
    cmdQueue.add({
        x: x,
        y: y,
        priority: (Math.abs(x) > 0.8 || Math.abs(y) > 0.8) ? 'critical' : 'normal'
    });
    
    // Actualizar display inmediatamente para responsividad visual
    updateJoystickDisplay(x, y);
}

// Funciones auxiliares para UI responsiva
function updateLatencyDisplay(latency) {
    const latencyEl = document.getElementById('latency');
    if (latencyEl) {
        latencyEl.textContent = `${Math.round(latency)}ms`;
        latencyEl.className = latency < 50 ? 'pill ok' : 
                             latency < 100 ? 'pill warning' : 'pill bad';
    }
}

function updateMotorStatus(motorA, motorB) {
    // Actualizar estado de motores en UI si existe
    const motorAEl = document.getElementById('motor-a-status');
    const motorBEl = document.getElementById('motor-b-status');
    
    if (motorAEl) {
        motorAEl.textContent = `A: ${motorA.speed || 0}% ${motorA.direction || 'stop'}`;
    }
    if (motorBEl) {
        motorBEl.textContent = `B: ${motorB.speed || 0}% ${motorB.direction || 'stop'}`;
    }
}

function updateJoystickDisplay(x, y) {
    // Actualización visual inmediata sin esperar respuesta del servidor
    const xEl = document.getElementById('joy-x');
    const yEl = document.getElementById('joy-y');
    
    if (xEl) xEl.textContent = x.toFixed(2);
    if (yEl) yEl.textContent = y.toFixed(2);
}

function pump(){
    sending = true; 
    pending = false;
    try { 
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(last)); 
            console.log(`📤 Enviado: x=${last.x.toFixed(2)}, y=${last.y.toFixed(2)}`);
        } else {
            console.warn('⚠️ WebSocket no está en estado OPEN');
            sending = false;
            wsOpen = false;
            return;
        }
    } catch(e){ 
        console.error('❌ Error enviando datos WebSocket:', e);
        sending = false; 
        wsOpen = false;
        return; 
    }
    // micro-cola: si llegó algo nuevo, manda otro frame en el próximo frame de pantalla
    requestAnimationFrame(()=>{
        sending = false;
        if (pending && wsOpen) pump();
    });
}

/* ====== Gamepad (HTML5) ====== */
let gpIndex = null;

function pollGamepad(){
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    let gp = gpIndex!==null ? pads[gpIndex] : null;
    if(!gp){ 
        for(let i=0;i<pads.length;i++){ 
            if(pads[i]){ 
                gp=pads[i]; 
                gpIndex=i; 
                break; 
            } 
        } 
    }
    
    document.getElementById('gpstat').textContent = gp ? `gamepad: ${gp.id}` : 'gamepad: —';
    
    if(gp){
        let x = gp.axes[0] || 0;
        // COMPORTAMIENTO TIPO DRONE: Y invertido para gamepad físico
        // Stick hacia arriba (valor negativo) = avanzar (valor positivo)
        let y = (gp.axes[1] || 0); // Mantener valor crudo para comportamiento drone
        const DZ = 0.06;
        if (Math.abs(x)<DZ) x=0;
        if (Math.abs(y)<DZ) y=0;
        
        if (!dragging){
            stick.x = Math.max(-1, Math.min(1, +x.toFixed(3)));
            stick.y = Math.max(-1, Math.min(1, +y.toFixed(3)));
            draw(); 
            sendXY(stick.x, stick.y);
        }
        
        // Botón B / O (id=1) -> stop
        if (gp.buttons && gp.buttons[1] && gp.buttons[1].pressed){ 
            stopAll(); 
        }
    }
    requestAnimationFrame(pollGamepad);
}

/* ====== HUD ====== */
function updateHUD(h){
    if(!h) return;
    document.getElementById('jx').textContent=(h.joy.x).toFixed(2);
    document.getElementById('jy').textContent=(h.joy.y).toFixed(2);
    document.getElementById('ml').textContent=(h.mix.left).toFixed(2);
    document.getElementById('mr').textContent=(h.mix.right).toFixed(2);
    document.getElementById('da').textContent=Math.round(h.A.speed);
    document.getElementById('db').textContent=Math.round(h.B.speed);
    document.getElementById('dira').textContent=h.A.dir;
    document.getElementById('dirb').textContent=h.B.dir;
}

function stopAll(){
    centerStick();
    fetch('/api/stop', {method:'POST'})
        .then(()=>fetch('/api/health'))
        .then(r=>r.json())
        .then(updateHUD);
}

/* Eventos del canvas */
pad.addEventListener('mousedown', e=>{
    dragging=true; 
    setStickFromEvent(e);
});

pad.addEventListener('mousemove', e=>{
    if(dragging) setStickFromEvent(e);
});

window.addEventListener('mouseup', ()=>{
    if(dragging){
        dragging=false; 
        centerStick();
    }
});

pad.addEventListener('touchstart', e=>{
    dragging=true; 
    setStickFromEvent(e); 
    e.preventDefault();
},{passive:false});

pad.addEventListener('touchmove',  e=>{
    if(dragging) setStickFromEvent(e); 
    e.preventDefault();
},{passive:false});

pad.addEventListener('touchend', ()=>{
    if(dragging){
        dragging=false; 
        centerStick();
    }
});

// Inicialización
draw(); 
connectWS(); 
requestAnimationFrame(pollGamepad);
