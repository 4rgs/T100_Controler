#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T100 Master (ESP32 Coordinator)
- Lee canales del receptor ELRS en la RPi
- Envía comandos seriales al ESP32 de Motores (tank <fb> <lr>)
- Envía comandos seriales al ESP32 de Cámara (cam <pan_raw> <tilt_raw>)
- Health-check al inicio y monitoreo básico
"""
import asyncio
import time
from typing import Optional, Dict, Tuple

from elrs_receiver_ultra_fast import ELRSReceiverUltraFast
from master.config_master import get_default_master_config, MasterConfig
from master.serial_link import SerialLink


class T100Master:
    def __init__(self, config: Optional[MasterConfig] = None):
        self.cfg = config or get_default_master_config()
        self.elrs = ELRSReceiverUltraFast()
        self.link_motor: Optional[SerialLink] = None
        self.link_cam: Optional[SerialLink] = None

        # Estado
        self.is_running = False
        self.last_channels_time = 0.0
        self.loop_count = 0

        # Tiempos de envío por dispositivo
        self._tank_period = 1.0 / max(1, self.cfg.tank_rate_hz)
        self._cam_period = 1.0 / max(1, self.cfg.cam_rate_hz)
        self._next_tank_ts = 0.0
        self._next_cam_ts = 0.0

    # ---------- Inicialización y Health-check ----------
    async def initialize(self) -> bool:
        print("🎛️ Iniciando T100 Master (ESP32 Coordinator)")
        # ELRS
        if not await self.elrs.initialize():
            print("❌ No se pudo inicializar ELRS")
            return False

        # Serial links
        self.link_motor = SerialLink(
            name=self.cfg.esp32_motor.name,
            candidate_ports=self.cfg.esp32_motor.candidate_ports,
            baud_rate=self.cfg.esp32_motor.baud_rate,
            write_timeout=self.cfg.write_timeout_s,
            read_timeout=self.cfg.read_timeout_s,
        )
        self.link_cam = SerialLink(
            name=self.cfg.esp32_cam.name,
            candidate_ports=self.cfg.esp32_cam.candidate_ports,
            baud_rate=self.cfg.esp32_cam.baud_rate,
            write_timeout=self.cfg.write_timeout_s,
            read_timeout=self.cfg.read_timeout_s,
        )

        motor_ok = self.link_motor.try_connect()
        cam_ok = self.link_cam.try_connect()

        # Health-check: status
        motor_status_ok = False
        cam_status_ok = False
        if motor_ok:
            motor_status_ok, resp = self.link_motor.cmd_status()
            print(f"🧪 MOTOR status: {resp}")
        else:
            print("❌ No se encontró ESP32 Motor")
        if cam_ok:
            cam_status_ok, resp = self.link_cam.cmd_status()
            print(f"🧪 CAM status: {resp}")
        else:
            print("❌ No se encontró ESP32 Cam")

        if not (motor_ok and cam_ok and motor_status_ok and cam_status_ok):
            print("⚠️  Advertencia: No todos los dispositivos respondieron a 'status'. Se reintentará en el bucle.")

        self._next_tank_ts = time.time()
        self._next_cam_ts = time.time()
        self.last_channels_time = time.time()
        return True

    # ---------- Helpers de mapeo ----------
    def _raw_to_norm(self, raw: int) -> float:
        # ELRS raw típico 172..1811 (11-bit mapeado)
        min_raw, max_raw = 172, 1811
        raw_clamped = max(min_raw, min(max_raw, int(raw)))
        norm01 = (raw_clamped - min_raw) / (max_raw - min_raw)
        return norm01 * 2.0 - 1.0  # -1..1

    def _get_tank_inputs(self, ch: Dict[str, float]) -> Tuple[float, float]:
        # Extraer canales mapeados y normalizar a -1..1
        ch_f = ch.get(self.cfg.channels.tank_forward_ch, 992)
        ch_t = ch.get(self.cfg.channels.tank_turn_ch, 992)
        fb = self._raw_to_norm(ch_f)
        lr = self._raw_to_norm(ch_t)
        return fb, lr

    def _get_cam_inputs(self, ch: Dict[str, float]) -> Tuple[int, int]:
        # Cámara usa valores RAW 172..1811
        pan_raw = int(ch.get(self.cfg.channels.cam_pan_ch, 992))
        tilt_raw = int(ch.get(self.cfg.channels.cam_tilt_ch, 992))
        # Clamp
        pan_raw = max(172, min(1811, pan_raw))
        tilt_raw = max(172, min(1811, tilt_raw))
        return pan_raw, tilt_raw

    # ---------- Bucle principal ----------
    async def run(self):
        if not await self.initialize():
            return False
        self.is_running = True
        print("✅ Master inicializado. Enviando a: MOTOR(tank) @ {}Hz | CAM @ {}Hz".format(
            self.cfg.tank_rate_hz, self.cfg.cam_rate_hz
        ))
        print("🛑 Parar: Ctrl+C")

        try:
            while self.is_running:
                loop_start = time.perf_counter()
                now = time.time()

                # Leer canales (no bloquear)
                channels = self.elrs.read_channels_ultra_fast()
                if channels:
                    self.last_channels_time = now

                # Enviar a MOTOR
                if now >= self._next_tank_ts:
                    self._next_tank_ts = now + self._tank_period
                    if self.link_motor and channels:
                        fb, lr = self._get_tank_inputs(channels)
                        self.link_motor.cmd_tank(fb, lr, debug=False)

                # Enviar a CAM
                if now >= self._next_cam_ts:
                    self._next_cam_ts = now + self._cam_period
                    if self.link_cam and channels:
                        pan_raw, tilt_raw = self._get_cam_inputs(channels)
                        self.link_cam.cmd_cam(pan_raw, tilt_raw)

                # Failsafe si no hay canales por > 1s
                if now - self.last_channels_time > 1.0:
                    if self.link_motor:
                        self.link_motor.cmd_stop()
                    if self.link_cam:
                        # Recentrar cámara suavemente
                        self.link_cam.send_command("center", expect_ok=False, retries=0)

                self.loop_count += 1

                # Sleep adaptativo para no saturar CPU
                elapsed = time.perf_counter() - loop_start
                await asyncio.sleep(max(0.001, 0.005 - elapsed))
        except KeyboardInterrupt:
            print("\n🛑 Interrupción de usuario")
        finally:
            await self.cleanup()
        return True

    async def cleanup(self):
        print("🧹 Limpiando Master...")
        self.is_running = False
        # Enviar stop a dispositivos
        if self.link_motor:
            self.link_motor.cmd_stop()
            self.link_motor.close()
        if self.link_cam:
            try:
                self.link_cam.send_command("center", expect_ok=False, retries=0)
            except Exception:
                pass
            self.link_cam.close()
        await self.elrs.cleanup()
        print("✅ Master limpiado")


async def main():
    master = T100Master()
    await master.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
