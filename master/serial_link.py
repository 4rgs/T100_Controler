#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serial link helper to talk to ESP32 devices using line-based ASCII protocol.
- Auto-detect ports from candidate list
- Robust write with retries
- Read responses until newline with timeout
- Convenience methods for tank and camera commands
"""
from __future__ import annotations
import time
import serial
import os
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SerialStats:
    port: str = ""
    baud: int = 0
    writes: int = 0
    reads: int = 0
    errors: int = 0
    last_response: str = ""


class SerialLink:
    def __init__(self, name: str, candidate_ports: List[str], baud_rate: int, write_timeout: float = 0.05, read_timeout: float = 0.1):
        self.name = name
        self.candidate_ports = candidate_ports
        self.baud_rate = baud_rate
        self.write_timeout = write_timeout
        self.read_timeout = read_timeout
        self.conn: Optional[serial.Serial] = None
        self.port: Optional[str] = None
        self.stats = SerialStats()

    def is_connected(self) -> bool:
        return self.conn is not None and self.conn.is_open

    def try_connect(self) -> bool:
        # Try each candidate port; if pattern with wildcard, skip here (no glob) but try exact only
        for port in self.candidate_ports:
            if "*" in port or "?" in port:
                # Try to expand glob-like paths under /dev/serial/by-id when available
                try:
                    base_dir = os.path.dirname(port)
                    pattern = os.path.basename(port)
                    if os.path.isdir(base_dir):
                        for fname in os.listdir(base_dir):
                            from fnmatch import fnmatch
                            if fnmatch(fname, pattern):
                                full = os.path.join(base_dir, fname)
                                if self._open(full):
                                    return True
                except Exception:
                    pass
                continue
            if os.path.exists(port):
                if self._open(port):
                    return True
        return False

    def _open(self, port: str) -> bool:
        try:
            self.conn = serial.Serial(
                port=port,
                baudrate=self.baud_rate,
                timeout=self.read_timeout,
                write_timeout=self.write_timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                rtscts=False,
                dsrdtr=False,
                xonxoff=False,
            )
            time.sleep(0.2)  # allow device to reset on open
            self.port = port
            self.stats.port = port
            self.stats.baud = self.baud_rate
            # Flush any banner text
            try:
                self.conn.reset_input_buffer()
                self.conn.reset_output_buffer()
            except Exception:
                pass
            print(f"🔌 {self.name}: conectado a {port} @ {self.baud_rate}")
            return True
        except Exception as e:
            self.conn = None
            return False

    def close(self):
        try:
            if self.conn and self.conn.is_open:
                self.conn.close()
        finally:
            self.conn = None
            self.port = None

    def send_command(self, cmd: str, expect_ok: bool = True, retries: int = 1) -> Tuple[bool, str]:
        """
        Send a single-line command, return (ok, response_text).
        If expect_ok is True, success when line starts with 'OK' or contains 'STATUS'.
        """
        last_err = ""
        for attempt in range(retries + 1):
            try:
                if not self.is_connected():
                    if not self.try_connect():
                        last_err = "no_connected"
                        time.sleep(0.2)
                        continue
                # Write
                self.conn.write((cmd.strip() + "\n").encode("utf-8"))
                self.stats.writes += 1
                # Read single line (best-effort)
                line = self.conn.readline().decode(errors="ignore").strip()
                self.stats.reads += 1
                if line:
                    self.stats.last_response = line
                if not expect_ok:
                    return True, line
                # Accept several success markers
                ok = line.startswith("OK") or line.startswith("STATUS") or line.startswith("Ready") or line == "OK"
                if ok:
                    return True, line
                # If response is empty, short wait and retry
                last_err = line or "empty"
            except Exception as e:
                self.stats.errors += 1
                last_err = str(e)
                self.close()
                time.sleep(0.1)
        return False, last_err

    # Convenience wrappers
    def cmd_status(self) -> Tuple[bool, str]:
        return self.send_command("status", expect_ok=True, retries=1)

    def cmd_stop(self) -> Tuple[bool, str]:
        return self.send_command("stop", expect_ok=True, retries=1)

    def cmd_tank(self, forward: float, turn: float, debug: bool = False) -> Tuple[bool, str]:
        parts = ["tank", f"{forward:.3f}", f"{turn:.3f}"]
        if debug:
            parts.append("debug")
        return self.send_command(" ".join(parts), expect_ok=False, retries=0)

    def cmd_cam(self, pan_raw: int, tilt_raw: int) -> Tuple[bool, str]:
        # esp32_servo_cam supports 'cam <pan> <tilt>' with raw 172..1811
        return self.send_command(f"cam {pan_raw} {tilt_raw}", expect_ok=False, retries=0)
