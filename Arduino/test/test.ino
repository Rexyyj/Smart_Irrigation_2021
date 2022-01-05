#include <LoRaCom.h>
#include <VariableTimedAction.h>

String appEui = "0000000000000000";
String appKey = "7782AD611823290CC281D369A2C5FBB9";
LoRaCom lora(appEui, appKey);

void setup() {
  Serial.begin(9600);
  while (!Serial)
    ;
  delay(1000);
  Serial.println("Test start");

  lora.connect();

  while (!lora.status){
    Serial.println(lora.errorMsg);
    delay(1000);
  }
  Serial.println("LoRa setup success");
  Serial.println("The device EUI is:");
  Serial.println(lora.get_device_eui());
}

void loop() {
  bool tmp;
  tmp = lora.send(13.45);
  // lora.receive("world");
  delay(10000);
  
}

