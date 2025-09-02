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

/* ====== WebSocket (last-write-wins) ====== */
let ws=null, wsOpen=false, last={x:0,y:0}, sending=false, pending=false;

function connectWS(){
    try{
        const proto = location.protocol === 'https:' ? 'wss' : 'ws';
        ws = new WebSocket(`${proto}://${location.host}/ws`);
        document.getElementById('wsstat').textContent = 'ws: conectando…';
        
        ws.onopen = ()=>{
            wsOpen=true; 
            document.getElementById('wsstat').textContent='ws: conectado'; 
            document.getElementById('wsstat').className='pill ok';
        };
        
        ws.onclose = ()=>{
            wsOpen=false; 
            document.getElementById('wsstat').textContent='ws: cerrado'; 
            document.getElementById('wsstat').className='pill bad';
            setTimeout(connectWS, 500);
        };
        
        ws.onerror = ()=>{
            wsOpen=false; 
            document.getElementById('wsstat').textContent='ws: error'; 
            document.getElementById('wsstat').className='pill bad';
            try{ws.close();}catch(e){}
        };
        
        ws.onmessage = (ev)=>{ 
            try{ 
                const h=JSON.parse(ev.data); 
                updateHUD(h); 
            }catch(e){} 
        };
    }catch(e){ 
        setTimeout(connectWS, 800); 
    }
}

function sendXY(x,y){
    last = {x,y};
    if(!wsOpen) return;        // si no hay ws, descarta (no encola)
    if(!sending){ 
        pump(); 
    } else { 
        pending = true; 
    }   // hay un frame más nuevo
}

function pump(){
    sending = true; 
    pending = false;
    try { 
        ws.send(JSON.stringify(last)); 
    } catch(e){ 
        sending = false; 
        return; 
    }
    // micro-cola: si llegó algo nuevo, manda otro frame en el próximo frame de pantalla
    requestAnimationFrame(()=>{
        sending = false;
        if (pending) pump();
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
        let y = -(gp.axes[1] || 0); // ↑ positivo (no invertido)
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
