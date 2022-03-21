#include "ArduinoLowPower.h"

void setup() {
  // put your setup code here, to run once:
  // pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  LowPower.deepSleep(10000);
  delay(3000);
  // put your main code here, to run repeatedly:
  // digitalWrite(LED_BUILTIN, HIGH); 
  // delay(1000);
  // digitalWrite(LED_BUILTIN, LOW); 
 
}
