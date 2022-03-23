#include <LoRaCom.h>
#include <VariableTimedAction.h>

String appEui = "0000000000000000";
String appKey = "7782AD611823290CC281D369A2C5FBB9";
LoRaCom lora(appEui, appKey);
uint8_t device_id = 0x03;
int update_period = 3; // s
float irrigation_speed = 0.5; // L/s

void setup() {

  pinMode(1, OUTPUT);

  Serial.begin(9600);
  delay(1000);
  Serial.println("Test start");
  lora.change_to_class_C();
  lora.connect();

  while (!lora.status){
    Serial.println(lora.errorMsg);
    delay(1000);
    Serial.println("Retry connection...");
    lora.connect();
  }
  Serial.println("LoRa setup success");
  Serial.println("The device EUI is:");
  Serial.println(lora.get_device_eui());
  lora.send_pump_status(device_id, '1');
}
float irrigation_amount=0;
float pre_irrigation_amount=0;
void loop() {
  Serial.println(irrigation_amount);
  
  int value=lora.get_receive();
  if (value >=0){
    irrigation_amount=value;
  }

  if (pre_irrigation_amount==0 && irrigation_amount>0){
    lora.send_pump_status(device_id, '2');
    digitalWrite(1, HIGH); 
  }

  if (pre_irrigation_amount>0 && irrigation_amount==0){
    lora.send_pump_status(device_id, '1');
    digitalWrite(1, LOW); 
  }

  pre_irrigation_amount = irrigation_amount;
  if (irrigation_amount>0){
    irrigation_amount=irrigation_amount-update_period*irrigation_speed;
    if (irrigation_amount<0){
      irrigation_amount=0;
    }
  }
  delay(update_period*1000);
}
