/*
  Modbus RTU connection with SEM2255 sensor

  Circuit:
   - MKR board
   - External 12-24 V power Supply
   - MKR 485 shield
     - GND connected to GND of the Modbus RTU sensor and the Power supply V-
     - Power supply V+ connected to V+ sensor and MKR 7-24V input
     - Y connected to A/Y of the Modbus RTU sensor (green)
     - Z connected to B/Z of the Modbus RTU sensor (blue)
     - Jumper positions
       - FULL set to OFF
       - Z \/\/ Y set to ON

  created 6 January 2022
  by Rex Yu 
  
  Email:  jiafish@outlook.com
  github: https://github.com/Rexyyj/Smart_Irrigation_2021
  Smart Irrigation Project in Poilitecnico di Torino
*/
#include <ArduinoModbus.h>
#include <LoRaCom.h>
#include "ArduinoLowPower.h"
#define UpdatePeriod 10 //seconds
#define LoRaON true
#define EndnodeID 3

int sensorNum=3;
int sensorID[3]={1,2,3};
float temperature[3];
float moisture[3];

String appEui = "0000000000000000";
String appKey = "22107E640249BEB8EB9379896316B464";
LoRaCom lora(appEui, appKey);

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(1, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); 
  digitalWrite(1, LOW); 
  // start the Serial communication
  Serial.begin(9600);
  // while (!Serial);

  Serial.println("Modbus Temperature Humidity Sensor");
  // start the Modbus RTU client
  if (!ModbusRTUClient.begin(4800)) {
    Serial.println("Failed to start Modbus RTU Client!");
    while (1);
  }
  Serial.println("The device EUI is:");
  Serial.println(lora.get_device_eui());
  // start LoRa communication
  if (LoRaON==true){
    lora.connect();
    int init_retry_counter=0;
    while (!lora.status){
      Serial.println(lora.errorMsg);
      delay(1000);
      lora.connect();
      init_retry_counter++;
      if (init_retry_counter>=3) break;
    }
  }

  Serial.println("Init succeed!");
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
  
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH); 
  digitalWrite(1, HIGH); 
  delay(1000);
  bool read_success=false;
  for (int i=0;i<sensorNum;i++){
    // send a Holding registers read request to (slave) id 1, for 2 registers
    delay(500);
    if (!ModbusRTUClient.requestFrom(sensorID[i], 2, 0x0000, 2)) {
      Serial.print("failed to read registers! ");
      Serial.println(ModbusRTUClient.lastError());
    } else {
      // If the request succeeds, the sensor sends the readings, that are
      // stored in the holding registers. The read() method can be used to
      // get the raw temperature and the humidity values.
      short rawMoistrue = ModbusRTUClient.read();
      short rawTemperature = ModbusRTUClient.read();

      // To get the temperature in Celsius and the humidity reading as
      // a percentage, divide the raw value by 10.0.
      temperature[i] = rawTemperature / 10.0;
      moisture[i] = rawMoistrue / 10.0;


      read_success=true;
      Serial.println("Read success!");
    }
    
  }
  for (int i=0;i<sensorNum;i++){
      Serial.println(temperature[i]);
      Serial.println(moisture[i]);
      Serial.println("");
  }
  if (LoRaON==true && read_success==true){
      lora.send_multi_layer(EndnodeID,temperature[0],temperature[1],temperature[2],moisture[0],moisture[1],moisture[2]);
      
    }


  digitalWrite(LED_BUILTIN, LOW);  
  digitalWrite(1, LOW);
  
 
  if (LoRaON==true){
    LowPower.deepSleep(UpdatePeriod*1000);
  }
  else{
    delay(UpdatePeriod*1000);
  }  
  
  if (LoRaON==true){
    lora.connect();
    int retry_counter=0;
    while (!lora.status){
      Serial.println(lora.errorMsg);
      delay(1000);
      lora.connect();
      retry_counter++;
      if (retry_counter>=3) break;
    }
  }
}
