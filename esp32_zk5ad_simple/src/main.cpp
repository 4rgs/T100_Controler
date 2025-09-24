#include <Arduino.h>
#include "config.h"
#include "ZK5ADDriver.h"
#include "CommandParser.h"

// Global components
ZK5ADDriver motor_driver;
CommandParser command_parser(&motor_driver);

// Timing variables
unsigned long last_led_blink = 0;
bool led_state = false;

void setup() {
    // Initialize serial for communication
    Serial.begin(SERIAL_BAUDRATE);
    delay(1000);  // Allow serial to initialize
    
    Serial.println("\n🚀 ESP32-S3 ZK-5AD Simple Driver Starting...");
    Serial.println("===============================================");
    
    // Initialize status LED
    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, HIGH);
    
    // Initialize motor driver
    Serial.println("\n🔧 Initializing ZK-5AD Driver...");
    
    if (!motor_driver.initialize()) {
        Serial.println("❌ Failed to initialize motor driver");
        while (1) {
            // Blink LED rapidly to indicate error
            digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
            delay(200);
        }
    }
    
    Serial.println("✅ Motor driver initialized successfully");
    
    // Print system configuration
    printSystemConfiguration();
    
    // Stop motors initially
    motor_driver.stopMotors();
    
    Serial.println("\n🎯 System Ready - Send commands via Serial");
    Serial.println("Type 'help' for available commands");
    Serial.println("===============================================\n");
    
    // Show help on startup
    command_parser.executeHelp();
}

void loop() {
    // Process serial commands
    command_parser.processSerial();
    
    // Blink status LED to show system is alive
    blinkStatusLED(1000);  // Slow blink = normal operation
    
    // Small delay to prevent overwhelming the system
    delay(1);
}

void blinkStatusLED(unsigned long interval_ms) {
    unsigned long current_time = millis();
    if (current_time - last_led_blink >= interval_ms) {
        last_led_blink = current_time;
        led_state = !led_state;
        digitalWrite(STATUS_LED_PIN, led_state);
    }
}

void printSystemConfiguration() {
    Serial.println("\n🔧 System Configuration:");
    Serial.println("Hardware:");
    Serial.println("  Motor A: GPIO " + String(MOTOR_A_IN1_PIN) + ", " + String(MOTOR_A_IN2_PIN));
    Serial.println("  Motor B: GPIO " + String(MOTOR_B_IN1_PIN) + ", " + String(MOTOR_B_IN2_PIN));
    Serial.println("  Status LED: GPIO " + String(STATUS_LED_PIN));
    
    Serial.println("Configuration:");
    Serial.println("  PWM Frequency: " + String(PWM_FREQUENCY) + " Hz");
    Serial.println("  Max PWM: " + String(MAX_PWM_PERCENT) + "%");
    Serial.println("  Direction Change Delay: " + String(DIRECTION_CHANGE_DELAY_MS) + "ms");
    Serial.println("  Deadband: " + String(DEADBAND_THRESHOLD * 100) + "%");
    Serial.println("  Serial Baudrate: " + String(SERIAL_BAUDRATE));
    
    Serial.println("Motor Configuration:");
    Serial.println("  Motor A: Power Factor=" + String(MOTOR_A_POWER_FACTOR) + 
                  ", Invert=" + String(MOTOR_A_INVERT ? "Yes" : "No"));
    Serial.println("  Motor B: Power Factor=" + String(MOTOR_B_POWER_FACTOR) + 
                  ", Invert=" + String(MOTOR_B_INVERT ? "Yes" : "No"));
}
