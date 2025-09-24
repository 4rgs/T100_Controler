#include <Arduino.h>
#include "ServoDriver.h"
#include "CommandParser.h"

ServoDriver servoDriver;
ServoCommandParser* parserPtr = nullptr;

void setup() {
  // Start USB CDC serial
  Serial.begin(115200);
  while (!Serial) { delay(10); }

  delay(100);
  Serial.println();
  Serial.println("========================================");
  Serial.println("📹 ESP32-S3 Servo Camera Controller");
  Serial.println("Board: ESP32-S3 DevKit C1");
  Serial.println("Pins: Pan=GPIO4, Tilt=GPIO17, 50Hz");
  Serial.println("Commands: type 'help' for usage");
  Serial.println("========================================");

  if (!servoDriver.initialize()) {
    Serial.println("ERROR: Failed to initialize servos");
  } else {
    Serial.println("✅ Servos initialized and centered");
  }

  parserPtr = new ServoCommandParser(&servoDriver);
}

void loop() {
  if (parserPtr) parserPtr->processSerial();
  // Keep loop responsive but light
  delay(5);
}
