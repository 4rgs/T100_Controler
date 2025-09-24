#ifndef SERVO_COMMAND_PARSER_H
#define SERVO_COMMAND_PARSER_H

#include <Arduino.h>
#include "ServoDriver.h"

struct CamCommand {
  String type;     // cam, center, status, help, stop
  float p1;        // param1 (pan raw)
  float p2;        // param2 (tilt raw)
  bool debug;      // optional debug flag
  bool valid;      // parsed ok
};

class ServoCommandParser {
 public:
  explicit ServoCommandParser(ServoDriver* drv);
  void processSerial();

 private:
  ServoDriver* driver;
  String input_buffer;
  unsigned long last_cmd_ms;

  CamCommand parse(const String& s);
  void exec(const CamCommand& c);

  // Command handlers
  void doCam(float pan_raw, float tilt_raw, bool debug);
  void doCenter();
  void doStatus();
  void doHelp();
  void doStop();

  void ok(const String& msg);
  void err(const String& msg);
};

#endif // SERVO_COMMAND_PARSER_H
