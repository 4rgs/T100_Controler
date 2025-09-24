#ifndef ZK5AD_DRIVER_H
#define ZK5AD_DRIVER_H

#include <Arduino.h>
#include "config.h"

class ZK5ADDriver {
private:
    // Motor status tracking
    MotorStatus motor_a_status;
    MotorStatus motor_b_status;
    
    // Direction change protection
    String motor_a_last_direction = "stop";
    String motor_b_last_direction = "stop";
    unsigned long motor_a_direction_change_time = 0;
    unsigned long motor_b_direction_change_time = 0;
    
    // PWM channels for ESP32
    uint8_t motor_a_in1_channel = 0;
    uint8_t motor_a_in2_channel = 1;
    uint8_t motor_b_in1_channel = 2;
    uint8_t motor_b_in2_channel = 3;
    
    // Initialization state
    bool is_initialized = false;
    
    // Private methods
    int setTA6586Motor(float speed, bool is_motor_a, bool debug = false);
    void applyDirectionChangeProtection(bool is_motor_a, const String& new_direction, bool debug = false);
    void setMotorBrake(bool is_motor_a);
    void debugPrint(const String& message);

public:
    ZK5ADDriver();
    ~ZK5ADDriver();
    
    // Initialization
    bool initialize();
    void cleanup();
    
    // Main control methods
    void tankDrive(float forward_backward, float left_right, bool debug = false);
    void stopMotors();
    void emergencyStop();
    
    // Individual motor control
    void setMotorA(float speed, bool debug = false);
    void setMotorB(float speed, bool debug = false);
    
    // Status methods
    MotorStatus getMotorAStatus() const { return motor_a_status; }
    MotorStatus getMotorBStatus() const { return motor_b_status; }
    bool isInitialized() const { return is_initialized; }
    
    // Test methods
    void testTA6586Drive();
    void testMotorIndividual(bool is_motor_a, float speed, int duration_ms = 2000);
    
    // Utility methods
    void printStatus();
    void printConfiguration();
};

#endif // ZK5AD_DRIVER_H
