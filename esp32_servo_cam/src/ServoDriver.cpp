#include "ServoDriver.h"

ServoDriver::ServoDriver()
: initialized(false) {
  pan_status = {90.0f, SERVO_CENTER_US, String("Pan")};
  tilt_status = {90.0f, SERVO_CENTER_US, String("Tilt")};
}

bool ServoDriver::initialize() {
  if (initialized) return true;

  // Configure PWM frequency for both servos
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  pan.setPeriodHertz(SERVO_FREQ_HZ);
  tilt.setPeriodHertz(SERVO_FREQ_HZ);

  bool aok = pan.attach(SERVO_PAN_PIN, SERVO_MIN_US, SERVO_MAX_US);
  bool bok = tilt.attach(SERVO_TILT_PIN, SERVO_MIN_US, SERVO_MAX_US);

  if (!aok || !bok) {
    initialized = false;
    return false;
  }

  centerServos();
  initialized = true;
  return true;
}

void ServoDriver::centerServos() {
  if (!initialized) {
    // If not attached yet, try to attach and then center
    // But keep it simple: write center if attached
  }
  pan.writeMicroseconds(SERVO_CENTER_US);
  tilt.writeMicroseconds(SERVO_CENTER_US);
  pan_status = {90.0f, SERVO_CENTER_US, String("Pan")};
  tilt_status = {90.0f, SERVO_CENTER_US, String("Tilt")};
}

void ServoDriver::cleanup() {
  if (!initialized) return;
  centerServos();
  delay(100);
  pan.detach();
  tilt.detach();
  initialized = false;
}

float ServoDriver::rawToAngle(int raw, bool invert) const {
  int r = raw;
  if (r < RAW_MIN) r = RAW_MIN;
  if (r > RAW_MAX) r = RAW_MAX;
  float normalized = float(r - RAW_MIN) / float(RAW_MAX - RAW_MIN); // 0..1
  float angle = normalized * 180.0f; // 0..180
  if (invert) angle = 180.0f - angle;
  return angle;
}

int ServoDriver::angleToPulse(float angle_deg) const {
  float a = clampf(angle_deg, 0.0f, 180.0f);
  float pulse_range = float(SERVO_MAX_US - SERVO_MIN_US);
  int us = int(float(SERVO_MIN_US) + (a / 180.0f) * pulse_range);
  return us;
}

int ServoDriver::writeServo(Servo &s, int /*pin*/, float angle_deg, const char *name, bool debug) {
  int us = angleToPulse(angle_deg);
  s.writeMicroseconds(us);
  if (debug) {
    Serial.print("   "); Serial.print(name);
    Serial.print(": "); Serial.print(angle_deg, 1);
    Serial.print("° -> "); Serial.print(us);
    Serial.println("us");
  }
  return us;
}

void ServoDriver::controlCamera(int pan_raw, int tilt_raw, bool debug, float &pan_deg_out, float &tilt_deg_out) {
  if (!initialized) {
    pan_deg_out = 90.0f;
    tilt_deg_out = 90.0f;
    return;
  }

  float pan_deg = rawToAngle(pan_raw, PAN_INVERT);
  float tilt_deg = rawToAngle(tilt_raw, TILT_INVERT);

  int pan_us = writeServo(pan, SERVO_PAN_PIN, pan_deg, "Pan", debug);
  int tilt_us = writeServo(tilt, SERVO_TILT_PIN, tilt_deg, "Tilt", debug);

  pan_status = {pan_deg, pan_us, String("Pan")};
  tilt_status = {tilt_deg, tilt_us, String("Tilt")};

  pan_deg_out = pan_deg;
  tilt_deg_out = tilt_deg;
}
