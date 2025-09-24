#include "ZK5ADDriver.h"

ZK5ADDriver::ZK5ADDriver() {
    debugPrint("🚗 ZK-5AD (TA6586) Driver initialized");
    debugPrint("   Motor A (Left): GPIO " + String(MOTOR_A_IN1_PIN) + ", " + String(MOTOR_A_IN2_PIN));
    debugPrint("   Motor B (Right): GPIO " + String(MOTOR_B_IN1_PIN) + ", " + String(MOTOR_B_IN2_PIN));
    debugPrint("   PWM Frequency: " + String(PWM_FREQUENCY) + " Hz");
    debugPrint("   🛡️  Current spike protection: " + String(DIRECTION_CHANGE_DELAY_MS) + "ms");
}

ZK5ADDriver::~ZK5ADDriver() {
    cleanup();
}

bool ZK5ADDriver::initialize() {
    debugPrint("🔧 Initializing ZK-5AD Driver...");
    
    // Configure PWM channels for motors
    // Motor A
    ledcSetup(motor_a_in1_channel, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcSetup(motor_a_in2_channel, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcAttachPin(MOTOR_A_IN1_PIN, motor_a_in1_channel);
    ledcAttachPin(MOTOR_A_IN2_PIN, motor_a_in2_channel);
    
    // Motor B
    ledcSetup(motor_b_in1_channel, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcSetup(motor_b_in2_channel, PWM_FREQUENCY, PWM_RESOLUTION);
    ledcAttachPin(MOTOR_B_IN1_PIN, motor_b_in1_channel);
    ledcAttachPin(MOTOR_B_IN2_PIN, motor_b_in2_channel);
    
    // Initialize motors in brake state (TA6586: H+H = BRAKE)
    setMotorBrake(true);  // Motor A
    setMotorBrake(false); // Motor B
    
    is_initialized = true;
    debugPrint("✅ ZK-5AD Driver initialized successfully");
    
    return true;
}

void ZK5ADDriver::cleanup() {
    if (is_initialized) {
        stopMotors();
        
        // Detach PWM pins
        ledcDetachPin(MOTOR_A_IN1_PIN);
        ledcDetachPin(MOTOR_A_IN2_PIN);
        ledcDetachPin(MOTOR_B_IN1_PIN);
        ledcDetachPin(MOTOR_B_IN2_PIN);
        
        is_initialized = false;
        debugPrint("🧹 ZK-5AD Driver cleaned up");
    }
}

void ZK5ADDriver::tankDrive(float forward_backward, float left_right, bool debug) {
    if (!is_initialized) {
        debugPrint("❌ Driver not initialized");
        return;
    }
    
    // Apply deadband
    if (abs(forward_backward) < DEADBAND_THRESHOLD) {
        forward_backward = 0.0f;
    }
    if (abs(left_right) < DEADBAND_THRESHOLD) {
        left_right = 0.0f;
    }
    
    // TANK DRIVE LOGIC (from Python version):
    // forward_backward controls base speed
    // left_right modifies each motor for steering
    
    float left_speed = forward_backward;   // Motor A (left)
    float right_speed = forward_backward;  // Motor B (right)
    
    // Apply steering
    if (left_right > 0) {  // Turn right
        left_speed += left_right;    // Left motor faster
        right_speed -= left_right;   // Right motor slower
    } else if (left_right < 0) {  // Turn left
        left_speed += left_right;    // Left motor slower (left_right is negative)
        right_speed -= left_right;   // Right motor faster
    }
    
    // Limit speeds to valid range
    left_speed = constrain(left_speed, -1.0f, 1.0f);
    right_speed = constrain(right_speed, -1.0f, 1.0f);
    
    if (debug) {
        debugPrint("🎮 Tank Drive Input: FB=" + String(forward_backward, 2) + 
                  " LR=" + String(left_right, 2));
        debugPrint("🔧 Calculated Speeds: Left=" + String(left_speed, 2) + 
                  " Right=" + String(right_speed, 2));
    }
    
    // Apply to motors
    int pwm_a = setTA6586Motor(left_speed, true, debug);
    int pwm_b = setTA6586Motor(right_speed, false, debug);
    
    if (debug) {
        debugPrint("🔧 TA6586 Control (effective): Motor A PWM=" + String(pwm_a) + 
                  " | Motor B PWM=" + String(pwm_b));
    }
}

void ZK5ADDriver::setMotorA(float speed, bool debug) {
    if (!is_initialized) return;
    setTA6586Motor(speed, true, debug);
}

void ZK5ADDriver::setMotorB(float speed, bool debug) {
    if (!is_initialized) return;
    setTA6586Motor(speed, false, debug);
}

int ZK5ADDriver::setTA6586Motor(float speed, bool is_motor_a, bool debug) {
    // Determine new direction
    String new_direction;
    if (abs(speed) < DEADBAND_THRESHOLD) {
        new_direction = "stop";
    } else if (speed > 0) {
        new_direction = "forward";
    } else {
        new_direction = "backward";
    }
    
    // Apply direction change protection
    applyDirectionChangeProtection(is_motor_a, new_direction, debug);
    
    // Get motor configuration
    bool invert = is_motor_a ? MOTOR_A_INVERT : MOTOR_B_INVERT;
    float power_factor = is_motor_a ? MOTOR_A_POWER_FACTOR : MOTOR_B_POWER_FACTOR;
    uint8_t in1_channel = is_motor_a ? motor_a_in1_channel : motor_b_in1_channel;
    uint8_t in2_channel = is_motor_a ? motor_a_in2_channel : motor_b_in2_channel;
    String motor_name = is_motor_a ? "A" : "B";
    
    // Stop motor if speed is zero - TA6586: H+H = BRAKE
    if (abs(speed) < DEADBAND_THRESHOLD) {
        ledcWrite(in1_channel, MAX_PWM_VALUE);  // HIGH (brake)
        ledcWrite(in2_channel, MAX_PWM_VALUE);  // HIGH (brake)
        
        // Update status
        MotorStatus& status = is_motor_a ? motor_a_status : motor_b_status;
        status.direction = "brake";
        status.power_percent = 0.0f;
        status.pwm_value = 0;
        status.last_update = millis();
        
        if (debug) {
            debugPrint("🛑 TA6586 Motor " + motor_name + ": BRAKE (H+H)");
        }
        return 0;
    }
    
    // Calculate PWM with power factor
    int pwm_final = (int)(abs(speed) * MAX_PWM_VALUE * power_factor * (MAX_PWM_PERCENT / 100.0f));
    pwm_final = constrain(pwm_final, 0, MAX_PWM_VALUE);
    
    // TA6586 Logic: PWM on one pin, 0 on the other for direction
    if (speed > 0) {
        // Forward direction
        if (invert) {
            // Inverted: IN2=PWM, IN1=0
            ledcWrite(in1_channel, 0);
            ledcWrite(in2_channel, pwm_final);
            if (debug) {
                debugPrint("▶️  TA6586 Motor " + motor_name + ": FORWARD (inverted) - IN1=0, IN2=" + String(pwm_final));
            }
        } else {
            // Normal: IN1=PWM, IN2=0
            ledcWrite(in1_channel, pwm_final);
            ledcWrite(in2_channel, 0);
            if (debug) {
                debugPrint("▶️  TA6586 Motor " + motor_name + ": FORWARD - IN1=" + String(pwm_final) + ", IN2=0");
            }
        }
    } else {
        // Backward direction
        if (invert) {
            // Inverted: IN1=PWM, IN2=0
            ledcWrite(in1_channel, pwm_final);
            ledcWrite(in2_channel, 0);
            if (debug) {
                debugPrint("◀️  TA6586 Motor " + motor_name + ": BACKWARD (inverted) - IN1=" + String(pwm_final) + ", IN2=0");
            }
        } else {
            // Normal: IN2=PWM, IN1=0
            ledcWrite(in1_channel, 0);
            ledcWrite(in2_channel, pwm_final);
            if (debug) {
                debugPrint("◀️  TA6586 Motor " + motor_name + ": BACKWARD - IN1=0, IN2=" + String(pwm_final));
            }
        }
    }
    
    // Update status
    MotorStatus& status = is_motor_a ? motor_a_status : motor_b_status;
    status.direction = new_direction;
    status.power_percent = abs(speed) * 100.0f;
    status.pwm_value = pwm_final;
    status.last_update = millis();
    
    return pwm_final;
}

void ZK5ADDriver::applyDirectionChangeProtection(bool is_motor_a, const String& new_direction, bool debug) {
    String& last_direction = is_motor_a ? motor_a_last_direction : motor_b_last_direction;
    unsigned long& direction_change_time = is_motor_a ? motor_a_direction_change_time : motor_b_direction_change_time;
    String motor_name = is_motor_a ? "A" : "B";
    
    // Check if direction change protection is needed
    if (last_direction != "stop" && 
        new_direction != "stop" && 
        last_direction != new_direction) {
        
        if (debug) {
            debugPrint("⚠️  Motor " + motor_name + ": Direction change " + last_direction + 
                      "->" + new_direction + " - Applying " + String(DIRECTION_CHANGE_DELAY_MS) + "ms pause");
        }
        
        // 1. Stop motor immediately
        setMotorBrake(is_motor_a);
        
        // 2. Wait for safety delay
        delay(DIRECTION_CHANGE_DELAY_MS);
        
        // 3. Continue with new direction
        if (debug) {
            debugPrint("✅ Motor " + motor_name + ": Pause completed, applying new direction");
        }
        
        direction_change_time = millis();
    }
    
    // Update last direction
    last_direction = new_direction;
}

void ZK5ADDriver::setMotorBrake(bool is_motor_a) {
    uint8_t in1_channel = is_motor_a ? motor_a_in1_channel : motor_b_in1_channel;
    uint8_t in2_channel = is_motor_a ? motor_a_in2_channel : motor_b_in2_channel;
    
    // TA6586: H+H = BRAKE (active braking)
    ledcWrite(in1_channel, MAX_PWM_VALUE);
    ledcWrite(in2_channel, MAX_PWM_VALUE);
}

void ZK5ADDriver::stopMotors() {
    if (!is_initialized) return;
    
    setMotorBrake(true);  // Motor A
    setMotorBrake(false); // Motor B
    
    motor_a_status.direction = "brake";
    motor_a_status.power_percent = 0.0f;
    motor_a_status.pwm_value = 0;
    motor_a_status.last_update = millis();
    
    motor_b_status.direction = "brake";
    motor_b_status.power_percent = 0.0f;
    motor_b_status.pwm_value = 0;
    motor_b_status.last_update = millis();
    
    debugPrint("🛑 Motors TA6586 stopped");
}

void ZK5ADDriver::emergencyStop() {
    stopMotors();
    debugPrint("🚨 EMERGENCY STOP ACTIVATED");
}

void ZK5ADDriver::debugPrint(const String& message) {
    Serial.println(message);
}

void ZK5ADDriver::printStatus() {
    debugPrint("\n📊 ZK-5AD Motor Status:");
    debugPrint("Motor A: " + motor_a_status.direction + " @ " + 
              String(motor_a_status.power_percent, 1) + "% (PWM: " + 
              String(motor_a_status.pwm_value) + ")");
    debugPrint("Motor B: " + motor_b_status.direction + " @ " + 
              String(motor_b_status.power_percent, 1) + "% (PWM: " + 
              String(motor_b_status.pwm_value) + ")");
}

void ZK5ADDriver::printConfiguration() {
    debugPrint("\n🔧 ZK-5AD Configuration:");
    debugPrint("PWM Frequency: " + String(PWM_FREQUENCY) + " Hz");
    debugPrint("Max PWM: " + String(MAX_PWM_PERCENT) + "%");
    debugPrint("Direction Change Delay: " + String(DIRECTION_CHANGE_DELAY_MS) + "ms");
    debugPrint("Deadband: " + String(DEADBAND_THRESHOLD * 100) + "%");
}

void ZK5ADDriver::testTA6586Drive() {
    if (!is_initialized) {
        debugPrint("❌ Driver ZK-5AD not initialized");
        return;
    }
    
    debugPrint("\n🧪 Test ZK-5AD (TA6586) Tank Drive");
    
    struct TestCase {
        float forward_back;
        float left_right;
        String description;
    };
    
    TestCase test_cases[] = {
        {0.0f, 0.0f, "Stopped"},
        {0.3f, 0.0f, "Forward slow"},
        {0.7f, 0.0f, "Forward fast"},
        {-0.3f, 0.0f, "Backward slow"},
        {-0.7f, 0.0f, "Backward fast"},
        {0.0f, 0.5f, "Turn right in place"},
        {0.0f, -0.5f, "Turn left in place"},
        {0.5f, 0.3f, "Forward + turn right"},
        {0.5f, -0.3f, "Forward + turn left"},
        {-0.5f, 0.3f, "Backward + turn right"},
        {-0.5f, -0.3f, "Backward + turn left"}
    };
    
    for (auto& test : test_cases) {
        debugPrint("\n📋 " + test.description);
        tankDrive(test.forward_back, test.left_right, true);
        delay(2000);
    }
    
    stopMotors();
    debugPrint("\n✅ Test TA6586 completed");
}
