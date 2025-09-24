#include "CommandParser.h"

CommandParser::CommandParser(ZK5ADDriver* motor_driver) {
    driver = motor_driver;
    input_buffer = "";
    last_command_time = 0;
}

void CommandParser::processSerial() {
    // Read available serial data
    while (Serial.available()) {
        char c = Serial.read();
        
        if (c == '\n' || c == '\r') {
            // Process complete command
            if (input_buffer.length() > 0) {
                Command cmd = parseCommand(input_buffer);
                if (cmd.valid) {
                    executeCommand(cmd);
                    last_command_time = millis();
                } else {
                    sendError("Invalid command format");
                }
                input_buffer = "";
            }
        } else if (c >= 32 && c <= 126) {  // Printable characters only
            input_buffer += c;
            
            // Prevent buffer overflow
            if (input_buffer.length() > 100) {
                input_buffer = "";
                sendError("Command too long");
            }
        }
    }
}

Command CommandParser::parseCommand(const String& cmd_string) {
    Command cmd;
    cmd.valid = false;
    cmd.debug = false;
    cmd.param1 = 0.0f;
    cmd.param2 = 0.0f;
    
    String trimmed = cmd_string;
    trimmed.trim();
    trimmed.toLowerCase();
    
    // Check for debug flag
    if (trimmed.endsWith(" debug") || trimmed.endsWith(" d")) {
        cmd.debug = true;
        int space_pos = trimmed.lastIndexOf(' ');
        trimmed = trimmed.substring(0, space_pos);
        trimmed.trim();
    }
    
    // Parse different command types
    if (trimmed == "stop" || trimmed == "s") {
        cmd.type = "stop";
        cmd.valid = true;
    }
    else if (trimmed == "status" || trimmed == "st") {
        cmd.type = "status";
        cmd.valid = true;
    }
    else if (trimmed == "test" || trimmed == "t") {
        cmd.type = "test";
        cmd.valid = true;
    }
    else if (trimmed == "help" || trimmed == "h" || trimmed == "?") {
        cmd.type = "help";
        cmd.valid = true;
    }
    else if (trimmed.startsWith("tank ") || trimmed.startsWith("td ")) {
        // Tank drive command: "tank <forward_backward> <left_right>"
        cmd.type = "tank";
        
        int first_space = trimmed.indexOf(' ');
        int second_space = trimmed.indexOf(' ', first_space + 1);
        
        if (first_space > 0 && second_space > first_space) {
            String fb_str = trimmed.substring(first_space + 1, second_space);
            String lr_str = trimmed.substring(second_space + 1);
            
            cmd.param1 = fb_str.toFloat();
            cmd.param2 = lr_str.toFloat();
            
            // Validate range
            if (cmd.param1 >= -1.0f && cmd.param1 <= 1.0f &&
                cmd.param2 >= -1.0f && cmd.param2 <= 1.0f) {
                cmd.valid = true;
            }
        }
    }
    else if (trimmed.startsWith("motor ") || trimmed.startsWith("m ")) {
        // Motor command: "motor <a|b> <speed>"
        cmd.type = "motor";
        
        int first_space = trimmed.indexOf(' ');
        int second_space = trimmed.indexOf(' ', first_space + 1);
        
        if (first_space > 0 && second_space > first_space) {
            String motor_str = trimmed.substring(first_space + 1, second_space);
            String speed_str = trimmed.substring(second_space + 1);
            
            if (motor_str == "a" || motor_str == "b") {
                cmd.param1 = (motor_str == "a") ? 0.0f : 1.0f;  // 0=A, 1=B
                cmd.param2 = speed_str.toFloat();
                
                // Validate range
                if (cmd.param2 >= -1.0f && cmd.param2 <= 1.0f) {
                    cmd.valid = true;
                }
            }
        }
    }
    
    return cmd;
}

void CommandParser::executeCommand(const Command& cmd) {
    if (cmd.type == "stop") {
        executeStop();
    }
    else if (cmd.type == "status") {
        executeStatus();
    }
    else if (cmd.type == "test") {
        executeTest();
    }
    else if (cmd.type == "help") {
        executeHelp();
    }
    else if (cmd.type == "tank") {
        executeTankDrive(cmd.param1, cmd.param2, cmd.debug);
    }
    else if (cmd.type == "motor") {
        char motor = (cmd.param1 == 0.0f) ? 'a' : 'b';
        executeMotorControl(motor, cmd.param2, cmd.debug);
    }
}

void CommandParser::executeTankDrive(float forward_backward, float left_right, bool debug) {
    if (!driver->isInitialized()) {
        sendError("Driver not initialized");
        return;
    }
    
    driver->tankDrive(forward_backward, left_right, debug);
    
    String response = "OK: Tank drive FB=" + String(forward_backward, 2) + 
                     " LR=" + String(left_right, 2);
    sendResponse(response);
}

void CommandParser::executeMotorControl(char motor, float speed, bool debug) {
    if (!driver->isInitialized()) {
        sendError("Driver not initialized");
        return;
    }
    
    if (motor == 'a') {
        driver->setMotorA(speed, debug);
    } else {
        driver->setMotorB(speed, debug);
    }
    
    String response = "OK: Motor " + String(motor) + " speed=" + String(speed, 2);
    sendResponse(response);
}

void CommandParser::executeStop() {
    if (!driver->isInitialized()) {
        sendError("Driver not initialized");
        return;
    }
    
    driver->stopMotors();
    sendResponse("OK: Motors stopped");
}

void CommandParser::executeStatus() {
    if (!driver->isInitialized()) {
        sendError("Driver not initialized");
        return;
    }
    
    MotorStatus motor_a = driver->getMotorAStatus();
    MotorStatus motor_b = driver->getMotorBStatus();
    
    Serial.println("STATUS:");
    Serial.println("Motor A: " + motor_a.direction + " @ " + 
                  String(motor_a.power_percent, 1) + "% (PWM: " + 
                  String(motor_a.pwm_value) + ")");
    Serial.println("Motor B: " + motor_b.direction + " @ " + 
                  String(motor_b.power_percent, 1) + "% (PWM: " + 
                  String(motor_b.pwm_value) + ")");
    Serial.println("Uptime: " + String(millis() / 1000) + "s");
    Serial.println("Free Heap: " + String(ESP.getFreeHeap()) + " bytes");
    Serial.println("OK");
}

void CommandParser::executeTest() {
    if (!driver->isInitialized()) {
        sendError("Driver not initialized");
        return;
    }
    
    sendResponse("Starting test sequence...");
    driver->testTA6586Drive();
    sendResponse("OK: Test completed");
}

void CommandParser::executeHelp() {
    Serial.println("ZK-5AD ESP32 Driver Commands:");
    Serial.println("==============================");
    Serial.println("Tank Drive:");
    Serial.println("  tank <fb> <lr>     - Tank drive control (-1.0 to 1.0)");
    Serial.println("  td <fb> <lr>       - Short form");
    Serial.println("");
    Serial.println("Individual Motors:");
    Serial.println("  motor a <speed>    - Control motor A (-1.0 to 1.0)");
    Serial.println("  motor b <speed>    - Control motor B (-1.0 to 1.0)");
    Serial.println("  m a <speed>        - Short form");
    Serial.println("");
    Serial.println("Control:");
    Serial.println("  stop               - Stop all motors");
    Serial.println("  s                  - Short form");
    Serial.println("");
    Serial.println("Information:");
    Serial.println("  status             - Show motor status");
    Serial.println("  st                 - Short form");
    Serial.println("  test               - Run test sequence");
    Serial.println("  t                  - Short form");
    Serial.println("  help               - Show this help");
    Serial.println("  h or ?             - Short form");
    Serial.println("");
    Serial.println("Debug:");
    Serial.println("  Add 'debug' or 'd' to any command for verbose output");
    Serial.println("");
    Serial.println("Examples:");
    Serial.println("  tank 0.5 0.0       - Forward at 50%");
    Serial.println("  tank 0.0 0.3       - Turn right in place");
    Serial.println("  tank -0.2 -0.1     - Backward + slight left");
    Serial.println("  motor a 0.7 debug  - Motor A forward 70% with debug");
    Serial.println("  stop                - Emergency stop");
    Serial.println("OK");
}

void CommandParser::sendResponse(const String& response) {
    Serial.println(response);
}

void CommandParser::sendError(const String& error) {
    Serial.println("ERROR: " + error);
}
