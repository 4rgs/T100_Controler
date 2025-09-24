#ifndef SERVO_DRIVER_H
#define SERVO_DRIVER_H

#include <Arduino.h>
#include <ESP32Servo.h>

struct ServoStatus {
  float position_degrees;  // 0-180
  int pulse_width;         // microseconds
  String name;             // "Pan" / "Tilt"
};

class ServoDriver {
 public:
  ServoDriver();
  bool initialize();
  void centerServos();
  void cleanup();
  bool isInitialized() const { return initialized; }

  // Control principal de cámara con valores raw ELRS (172-1811)
  // Retorna posiciones (pan_deg, tilt_deg)
  void controlCamera(int pan_raw, int tilt_raw, bool debug, float &pan_deg_out, float &tilt_deg_out);

  // Estados
  ServoStatus getPanStatus() const { return pan_status; }
  ServoStatus getTiltStatus() const { return tilt_status; }

 private:
  // Pines (ESP32-S3 DevKit C1)
  // Basado en memoria del sistema: Servo control on GPIO 4 (Pan) y GPIO 17 (Tilt)
  static constexpr int SERVO_PAN_PIN = 4;
  static constexpr int SERVO_TILT_PIN = 17;

  // Rango de pulsos MG90S (us)
  static constexpr int SERVO_MIN_US = 500;   // puede ajustarse 500-600
  static constexpr int SERVO_CENTER_US = 1500;
  static constexpr int SERVO_MAX_US = 2400;  // puede ajustarse 2300-2400

  // Inversiones opcionales
  static constexpr bool PAN_INVERT = false;
  static constexpr bool TILT_INVERT = false;

  // Rango RAW típico ELRS
  static constexpr int RAW_MIN = 172;
  static constexpr int RAW_MAX = 1811;

  // Frecuencia de servos
  static constexpr int SERVO_FREQ_HZ = 50;   // MG90S

  Servo pan;
  Servo tilt;
  bool initialized;

  ServoStatus pan_status;
  ServoStatus tilt_status;

  // Utilidades
  static float clampf(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
  }

  float rawToAngle(int raw, bool invert) const;
  int angleToPulse(float angle_deg) const; // 0-180 -> us
  int writeServo(Servo &s, int pin, float angle_deg, const char *name, bool debug);
};

#endif // SERVO_DRIVER_H
