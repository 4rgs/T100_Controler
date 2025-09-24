#include "CommandParser.h"

ServoCommandParser::ServoCommandParser(ServoDriver* drv)
: driver(drv), input_buffer(""), last_cmd_ms(0) {}

void ServoCommandParser::processSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (input_buffer.length() > 0) {
        CamCommand cmd = parse(input_buffer);
        if (cmd.valid) {
          exec(cmd);
          last_cmd_ms = millis();
        } else {
          err("Invalid command");
        }
        input_buffer = "";
      }
    } else if (c >= 32 && c <= 126) {
      input_buffer += c;
      if (input_buffer.length() > 120) {
        input_buffer = "";
        err("Command too long");
      }
    }
  }
}

CamCommand ServoCommandParser::parse(const String& s) {
  CamCommand c; c.valid = false; c.debug = false; c.p1 = 0; c.p2 = 0; c.type = "";

  String t = s; t.trim(); t.toLowerCase();

  // debug flag
  if (t.endsWith(" debug") || t.endsWith(" d")) {
    c.debug = true;
    int sp = t.lastIndexOf(' ');
    if (sp > 0) t = t.substring(0, sp);
    t.trim();
  }

  if (t == "help" || t == "h" || t == "?") {
    c.type = "help"; c.valid = true; return c;
  }
  if (t == "status" || t == "st") {
    c.type = "status"; c.valid = true; return c;
  }
  if (t == "center" || t == "c") {
    c.type = "center"; c.valid = true; return c;
  }
  if (t == "stop" || t == "s") {
    c.type = "stop"; c.valid = true; return c;
  }

  if (t.startsWith("cam ") || t.startsWith("camera ") || t.startsWith("pt ")) {
    c.type = "cam";
    int sp1 = t.indexOf(' ');
    int sp2 = t.indexOf(' ', sp1 + 1);
    if (sp1 > 0 && sp2 > sp1) {
      String p1s = t.substring(sp1 + 1, sp2);
      String p2s = t.substring(sp2 + 1);
      c.p1 = p1s.toFloat();
      c.p2 = p2s.toFloat();
      // allow raw 172..1811 or normalized -1..1; detect range
      if (c.p1 >= 100 && c.p2 >= 100) {
        // assume raw
        if (c.p1 >= 100 && c.p1 <= 2000 && c.p2 >= 100 && c.p2 <= 2000) c.valid = true;
      } else {
        // assume normalized -1..1, convert to raw
        if (c.p1 >= -1.0f && c.p1 <= 1.0f && c.p2 >= -1.0f && c.p2 <= 1.0f) {
          // map -1..1 -> RAW_MIN..RAW_MAX (use constants from ServoDriver.h)
          const int RAW_MIN = 172; const int RAW_MAX = 1811;
          auto mapf = [&](float v){ return float(RAW_MIN) + (v + 1.0f) * 0.5f * float(RAW_MAX - RAW_MIN); };
          c.p1 = mapf(c.p1);
          c.p2 = mapf(c.p2);
          c.valid = true;
        }
      }
    }
    return c;
  }

  return c;
}

void ServoCommandParser::exec(const CamCommand& c) {
  if (c.type == "help") { doHelp(); return; }
  if (c.type == "status") { doStatus(); return; }
  if (c.type == "center") { doCenter(); return; }
  if (c.type == "stop") { doStop(); return; }
  if (c.type == "cam") { doCam((int)c.p1, (int)c.p2, c.debug); return; }
}

void ServoCommandParser::doCam(float pan_raw, float tilt_raw, bool debug) {
  if (!driver->isInitialized()) { err("Driver not initialized"); return; }
  float pan_deg=0, tilt_deg=0;
  driver->controlCamera((int)pan_raw, (int)tilt_raw, debug, pan_deg, tilt_deg);
  String resp = "OK: Cam Pan=" + String(pan_deg, 1) + "° Tilt=" + String(tilt_deg, 1) + "°";
  ok(resp);
}

void ServoCommandParser::doCenter() {
  if (!driver->isInitialized()) { err("Driver not initialized"); return; }
  driver->centerServos();
  ok("OK: Servos centered");
}

void ServoCommandParser::doStatus() {
  if (!driver->isInitialized()) { err("Driver not initialized"); return; }
  ServoStatus ps = driver->getPanStatus();
  ServoStatus ts = driver->getTiltStatus();
  Serial.println("STATUS:");
  Serial.println("Pan: " + String(ps.position_degrees,1) + "° (" + String(ps.pulse_width) + "us)");
  Serial.println("Tilt: " + String(ts.position_degrees,1) + "° (" + String(ts.pulse_width) + "us)");
  Serial.println("Uptime: " + String(millis()/1000) + "s");
  Serial.println("Free Heap: " + String(ESP.getFreeHeap()) + " bytes");
  Serial.println("OK");
}

void ServoCommandParser::doHelp() {
  Serial.println("ESP32 Servo Camera Commands:");
  Serial.println("============================");
  Serial.println("Camera Control:");
  Serial.println("  cam <pan> <tilt>    - Raw 172..1811 or normalized -1..1");
  Serial.println("  pt <pan> <tilt>     - Alias");
  Serial.println("");
  Serial.println("Utilities:");
  Serial.println("  center              - Center both servos");
  Serial.println("  status              - Show status");
  Serial.println("  help                - Show this help");
  Serial.println("  stop                - Same as center");
  Serial.println("");
  Serial.println("Debug:");
  Serial.println("  Add 'debug' or 'd' to any command for verbose output");
  Serial.println("OK");
}

void ServoCommandParser::doStop() {
  doCenter();
}

void ServoCommandParser::ok(const String& msg) {
  Serial.println(msg);
}

void ServoCommandParser::err(const String& msg) {
  Serial.println("ERROR: " + msg);
}
