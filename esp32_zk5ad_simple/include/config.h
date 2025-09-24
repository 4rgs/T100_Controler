#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// Hardware Configuration - Anti-Interference Pin Mapping
// Based on physical separation strategy from Python version

// Motor A (Left) - Hardware PWM + Digital separation
#define MOTOR_A_IN1_PIN     18  // Hardware PWM0
#define MOTOR_A_IN2_PIN     24  // Digital pin, opposite corner
#define MOTOR_A_INVERT      false
#define MOTOR_A_POWER_FACTOR 0.9f

// Motor B (Right) - Hardware PWM + Digital separation  
#define MOTOR_B_IN1_PIN     19  // Hardware PWM1
#define MOTOR_B_IN2_PIN     25  // Digital pin, opposite corner
#define MOTOR_B_INVERT      true
#define MOTOR_B_POWER_FACTOR 0.9f

// PWM Configuration - Anti-interference settings
#define PWM_FREQUENCY       2000    // Reduced frequency for less EMI
#define PWM_RESOLUTION      8       // 8-bit resolution (0-255)
#define MAX_PWM_PERCENT     90.0f   // Limited power for noise reduction
#define MAX_PWM_VALUE       255

// Timing Configuration - Current spike protection
#define DIRECTION_CHANGE_DELAY_MS   100     // Protection delay

// Safety Configuration
#define DEADBAND_THRESHOLD      0.05f   // 5% deadband

// Serial Configuration
#define SERIAL_BAUDRATE     115200
#define COMMAND_TIMEOUT_MS  1000    // 1 second command timeout

// Status LED
#define STATUS_LED_PIN      2   // Built-in LED on ESP32-S3

// Motor Status Structure
struct MotorStatus {
    String direction = "stop";
    float power_percent = 0.0f;
    int pwm_value = 0;
    unsigned long last_update = 0;
};

#endif // CONFIG_H
