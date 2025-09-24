#ifndef COMMAND_PARSER_H
#define COMMAND_PARSER_H

#include <Arduino.h>
#include "ZK5ADDriver.h"

// Command structure
struct Command {
    String type;
    float param1;
    float param2;
    bool debug;
    bool valid;
};

class CommandParser {
private:
    ZK5ADDriver* driver;
    String input_buffer;
    unsigned long last_command_time;
    
    // Private methods
    Command parseCommand(const String& cmd_string);
    void executeCommand(const Command& cmd);
    void sendResponse(const String& response);
    void sendError(const String& error);

public:
    CommandParser(ZK5ADDriver* motor_driver);
    
    // Main processing method
    void processSerial();
    
    // Command execution methods
    void executeTankDrive(float forward_backward, float left_right, bool debug = false);
    void executeMotorControl(char motor, float speed, bool debug = false);
    void executeStop();
    void executeStatus();
    void executeTest();
    void executeHelp();
};

#endif // COMMAND_PARSER_H
