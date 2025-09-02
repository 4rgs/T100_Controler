#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Joystick (virtual + físico) con WebSocket — Raspberry Pi + L298N (pigpio + PWM DMA)

Pinout (config por defecto del usuario):
- Motor A (izq):  ENA=GPIO12, IN1=GPIO16, IN2=GPIO20
- Motor B (der):  ENB=GPIO26, IN3=GPIO19, IN4=GPIO21
- INVERT_A=False, INVERT_B=False
- Eje Y NO invertido (arriba=positivo)

Mezcla diferencial: left = y + x, right = y - x  (clamp −1..1)
"""

import atexit
import json
import signal
import time

from flask import Flask, jsonify, render_template_string, request
from flask_sock import Sock
import pigpio

# ====== CONFIG ======
ENA, IN1, IN2 = 12, 16, 20         # Motor A (izq)
ENB, IN3, IN4 = 26, 19, 21         # Motor B (der)
INVERT_A = False
INVERT_B = False
PWM_FREQ = 1000            # Hz (1–4 kHz va bien)
JOYSTICK_DEADZONE = 0.03   # zona muerta x,y (antes 0.10)
NON_LINEAR = 1.0           # 1.0 = lineal (antes 1.2)
HTTP_PORT = 8080
# =====================

app = Flask(__name__)
sock = Sock(app)

# ---------- pigpio ----------
pi = pigpio.pi()
if not pi.connected:
    raise SystemExit("❌ No puedo conectar a pigpio. Ejecuta: sudo systemctl enable --now pigpiod")

# Modo pines
for p in (IN1, IN2, IN3, IN4, ENA, ENB):
    pi.set_mode(p, pigpio.OUTPUT)
    pi.write(p, 0)

# PWM DMA en ENA/ENB
for p in (ENA, ENB):
    pi.set_PWM_frequency(p, PWM_FREQ)
    pi.set_PWM_dutycycle(p, 0)

state = {
    "A": {"dir": "coast", "speed": 0.0, "invert": INVERT_A},  # speed en %
    "B": {"dir": "coast", "speed": 0.0, "invert": INVERT_B},
    "joy": {"x": 0.0, "y": 0.0},  # -1..1
    "mix": {"left": 0.0, "right": 0.0},
    "last_ts": 0.0
}

def _drive(pin_h, pin_l, a, b):
    pi.write(pin_h, 1 if a else 0)
    pi.write(pin_l, 1 if b else 0)

def _apply_dir(which: str, forward: bool, brake: bool = False):
    if which == "A":
        if brake:
            _drive(IN1, IN2, 1, 1); state["A"]["dir"] = "brake"; return
        fwd = forward ^ INVERT_A
        if fwd:  _drive(IN1, IN2, 1, 0); state["A"]["dir"] = "fwd"
        else:    _drive(IN1, IN2, 0, 1); state["A"]["dir"] = "back"
    else:
        if brake:
            _drive(IN3, IN4, 1, 1); state["B"]["dir"] = "brake"; return
        fwd = forward ^ INVERT_B
        if fwd:  _drive(IN3, IN4, 1, 0); state["B"]["dir"] = "fwd"
        else:    _drive(IN3, IN4, 0, 1); state["B"]["dir"] = "back"

def _set_duty(which: str, duty_pct: float):
    dc255 = max(0, min(255, int(duty_pct * 2.55)))
    if which == "A":
        pi.set_PWM_dutycycle(ENA, dc255); state["A"]["speed"] = duty_pct
    else:
        pi.set_PWM_dutycycle(ENB, dc255); state["B"]["speed"] = duty_pct

def _coast(which: str):
    if which == "A":
        _drive(IN1, IN2, 0, 0); pi.set_PWM_dutycycle(ENA, 0)
        state["A"].update({"dir": "coast", "speed": 0.0})
    else:
        _drive(IN3, IN4, 0, 0); pi.set_PWM_dutycycle(ENB, 0)
        state["B"].update({"dir": "coast", "speed": 0.0})

def all_stop():
    _coast("A"); _coast("B")

def _cleanup(*_):
    try: all_stop()
    finally: pi.stop()

atexit.register(_cleanup)
signal.signal(signal.SIGINT, _cleanup)
signal.signal(signal.SIGTERM, _cleanup)

# ---- Mezcla con shaping ----
def _shape(v: float) -> float:
    if v == 0: return 0.0
    s = 1.0 if v > 0 else -1.0
    return s * (abs(v) ** NON_LINEAR)

def _apply_joystick(x: float, y: float):
    # zona muerta + curva (y>0 = avanzar, NO invertido)
    x = 0.0 if abs(x) < JOYSTICK_DEADZONE else _shape(x)
    y = 0.0 if abs(y) < JOYSTICK_DEADZONE else _shape(y)

    # mezcla diferencial
    left  = max(-1.0, min(1.0, y + x))
    right = max(-1.0, min(1.0, y - x))

    # Motor A (izq)
    if left == 0.0: _coast("A")
    else: _apply_dir("A", forward=(left > 0)); _set_duty("A", abs(left) * 100.0)

    # Motor B (der)
    if right == 0.0: _coast("B")
    else: _apply_dir("B", forward=(right > 0)); _set_duty("B", abs(right) * 100.0)

    # estado
    state["joy"]["x"] = x; state["joy"]["y"] = y
    state["mix"]["left"] = left; state["mix"]["right"] = right
    state["last_ts"] = time.time()

    # ---- LOG para depurar respuesta ----
    print(f"[JOY] x={x:.2f} y={y:.2f} -> L={left:.2f} R={right:.2f} "
          f"A:{state['A']['dir']}@{state['A']['speed']:.0f}% "
          f"B:{state['B']['dir']}@{state['B']['speed']:.0f}%",
          flush=True)

# -------------------- UI --------------------
HTML = """<!doctype html><meta charset="utf-8">
<title>Joystick L298N · WS</title>
<style>
  body{font-family:system-ui;background:#0b0b0e;color:#eaeaea;margin:0}
  .wrap{max-width:980px;margin:24px auto;padding:0 12px}
  .card{background:#141419;border:1px solid #242433;border-radius:14px;padding:14px 16px;margin:10px 0}
  .row{display:flex;gap:16px;flex-wrap:wrap}
  .col{flex:1 1 280px}
  .btn{border:1px solid #2f2f42;background:#1c1c27;color:#eaeaea;padding:10px 12px;border-radius:10px;cursor:pointer}
  .btn:active{transform:scale(.98)}
  .muted{color:#9aa0aa}
  .meter{font-variant-numeric:tabular-nums}
  #pad{touch-action:none;background:#0e0e14;border:1px solid #242433;border-radius:12px;display:block;margin:auto}
  .pill{display:inline-block;padding:4px 8px;border:1px solid #2f2f42;border-radius:999px;background:#1c1c27}
  .ok{color:#9be49b} .bad{color:#e49b9b}
</style>

<div class="wrap">
  <h1>Joystick · L298N <span class="pill" id="wsstat">ws: …</span> <span class="pill" id="gpstat">gamepad: —</span></h1>
  <div class="row">
    <div class="col">
      <div class="card">
        <h2>Palanca (mouse/touch o gamepad)</h2>
        <canvas id="pad" width="300" height="300"></canvas>
        <p class="muted">Centro = stop · Arriba = avanzar · Abajo = retroceder · Izq/Der = giro en el sitio.<br>
        Gamepad: stick izquierdo; botón B/○ detiene todo.</p>
        <div><button class="btn" onclick="stopAll()">🛑 Detener todo</button></div>
      </div>
    </div>
    <div class="col">
      <div class="card">
        <h2>Estado</h2>
        <div class="meter">
          Joystick: x=<span id="jx">0.00</span> · y=<span id="jy">0.00</span><br>
          Mix L/R: <span id="ml">0.00</span> / <span id="mr">0.00</span><br>
          Duty A/B: <span id="da">0</span>% / <span id="db">0</span>%<br>
          Dir A/B: <span id="dira">coast</span> / <span id="dirb">coast</span>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
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
  let px,py; if(e.touches&&e.touches.length){px=e.touches[0].clientX;py=e.touches[0].clientY;} else {px=e.clientX;py=e.clientY;}
  let dx=px-cx, dy=py-cy; const mag=Math.hypot(dx,dy), max=R; if(mag>max){dx=dx*max/mag; dy=dy*max/mag;}
  stick.x=+(dx/R).toFixed(3);
  stick.y=+(-dy/R).toFixed(3);  // ↑ positivo (NO invertido)
  draw(); sendXY(stick.x, stick.y);
}
function centerStick(){ stick.x=0; stick.y=0; draw(); sendXY(0,0); }

/* ====== WebSocket (last-write-wins) ====== */
let ws=null, wsOpen=false, last={x:0,y:0}, sending=false, pending=false;
function connectWS(){
  try{
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    ws = new WebSocket(`${proto}://${location.host}/ws`);
    document.getElementById('wsstat').textContent = 'ws: conectando…';
    ws.onopen = ()=>{
      wsOpen=true; document.getElementById('wsstat').textContent='ws: conectado'; document.getElementById('wsstat').className='pill ok';
    };
    ws.onclose = ()=>{
      wsOpen=false; document.getElementById('wsstat').textContent='ws: cerrado'; document.getElementById('wsstat').className='pill bad';
      setTimeout(connectWS, 500);
    };
    ws.onerror = ()=>{
      wsOpen=false; document.getElementById('wsstat').textContent='ws: error'; document.getElementById('wsstat').className='pill bad';
      try{ws.close();}catch(e){}
    };
    ws.onmessage = (ev)=>{ try{ const h=JSON.parse(ev.data); updateHUD(h); }catch(e){} };
  }catch(e){ setTimeout(connectWS, 800); }
}
function sendXY(x,y){
  last = {x,y};
  if(!wsOpen) return;        // si no hay ws, descarta (no encola)
  if(!sending){ pump(); }
  else { pending = true; }   // hay un frame más nuevo
}
function pump(){
  sending = true; pending = false;
  try { ws.send(JSON.stringify(last)); }
  catch(e){ sending = false; return; }
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
  if(!gp){ for(let i=0;i<pads.length;i++){ if(pads[i]){ gp=pads[i]; gpIndex=i; break; } } }
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
      draw(); sendXY(stick.x, stick.y);
    }
    // Botón B / O (id=1) -> stop
    if (gp.buttons && gp.buttons[1] && gp.buttons[1].pressed){ stopAll(); }
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
  fetch('/api/stop', {method:'POST'}).then(()=>fetch('/api/health').then(r=>r.json()).then(updateHUD));
}

/* Eventos del canvas */
pad.addEventListener('mousedown', e=>{dragging=true; setStickFromEvent(e);});
pad.addEventListener('mousemove', e=>{if(dragging) setStickFromEvent(e);});
window.addEventListener('mouseup', ()=>{if(dragging){dragging=false; centerStick();}});
pad.addEventListener('touchstart', e=>{dragging=true; setStickFromEvent(e); e.preventDefault();},{passive:false});
pad.addEventListener('touchmove',  e=>{if(dragging) setStickFromEvent(e); e.preventDefault();},{passive:false});
pad.addEventListener('touchend',   ()=>{if(dragging){dragging=false; centerStick();}});

draw(); connectWS(); requestAnimationFrame(pollGamepad);
</script>
"""

@app.get("/")
def index():
    return render_template_string(HTML)

@app.get("/api/health")
def api_health():
    return jsonify({
        "A": {"dir": state["A"]["dir"], "speed": state["A"]["speed"],
              "duty": int(state["A"]["speed"]*2.55)},
        "B": {"dir": state["B"]["dir"], "speed": state["B"]["speed"],
              "duty": int(state["B"]["speed"]*2.55)},
        "joy": state["joy"], "mix": state["mix"], "ts": state["last_ts"]
    })

@app.post("/api/stop")
def api_stop():
    all_stop()
    state["joy"]["x"] = 0.0; state["joy"]["y"] = 0.0
    state["mix"]["left"] = 0.0; state["mix"]["right"] = 0.0
    return jsonify(ok=True)

# -------- WebSocket: recibe {x,y} y responde estado ligero para HUD ------
@sock.route('/ws')
def ws_route(ws):
    while True:
        try:
            msg = ws.receive()
            if msg is None:
                break
            # Acepta texto o binario
            if isinstance(msg, (bytes, bytearray)):
                try: msg = msg.decode('utf-8')
                except: continue
            try:
                d = json.loads(msg)
            except Exception:
                continue
            x = max(-1.0, min(1.0, float(d.get("x", 0.0))))
            y = max(-1.0, min(1.0, float(d.get("y", 0.0))))
            _apply_joystick(x, y)
            ws.send(json.dumps({
                "A": {"dir": state["A"]["dir"], "speed": state["A"]["speed"]},
                "B": {"dir": state["B"]["dir"], "speed": state["B"]["speed"]},
                "joy": state["joy"], "mix": state["mix"]
            }))
        except Exception:
            break

# --------- Endpoint HTTP para test rápido del backend ----------
@app.post("/api/joy")
def api_joy_http():
    d = request.get_json(force=True) or {}
    try:
        x = max(-1.0, min(1.0, float(d.get("x", 0.0))))
        y = max(-1.0, min(1.0, float(d.get("y", 0.0))))
    except Exception:
        return jsonify(ok=False, err="bad payload"), 400
    _apply_joystick(x, y)
    return jsonify(ok=True, state={
        "A": state["A"], "B": state["B"], "joy": state["joy"], "mix": state["mix"]
    })

if __name__ == "__main__":
    # Nota: flask-sock usa werkzeug; para producción, pon un reverse proxy (nginx/caddy) si quieres HTTPS/WSS
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False, threaded=True)