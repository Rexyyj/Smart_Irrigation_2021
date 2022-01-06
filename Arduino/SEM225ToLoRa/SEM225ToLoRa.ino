/*
  Modbus RTU connection with SEM225 sensor

  Circuit:
   - MKR board
   - External 12-24 V power Supply
   - MKR 485 shield
     - GND connected to GND of the Modbus RTU sensor and the Power supply V-
     - Power supply V+ connected to V+ sensor and MKR 7-24V input
     - Y connected to A/Y of the Modbus RTU sensor
     - Z connected to B/Z of the Modbus RTU sensor
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

#define UpdatePeriod 10 //seconds
#define SensorId 1

float temperature;
float moisture;

String appEui = "0000000000000000";
String appKey = "FE756C6D733663AC72B081EA8DEEE11C";
LoRaCom lora(appEui, appKey);

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); 
  // start the Serial communication
  Serial.begin(9600);
  // while (!Serial);

  Serial.println("Modbus Temperature Humidity Sensor");
  // start the Modbus RTU client
  if (!ModbusRTUClient.begin(9600)) {
    Serial.println("Failed to start Modbus RTU Client!");
    while (1);
  }
  Serial.println("The device EUI is:");
  Serial.println(lora.get_device_eui());
  // start LoRa communication
  lora.connect();
  while (!lora.status){
    Serial.println(lora.errorMsg);
    delay(1000);
  }
  Serial.println("Init succeed!");
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
  
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH); 
  // send a Holding registers read request to (slave) id 1, for 2 registers
  if (!ModbusRTUClient.requestFrom(SensorId, 2, 0x0012, 2)) {
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
    temperature = rawTemperature / 10.0;
    moisture = rawMoistrue / 10.0;

    Serial.println(temperature);
    Serial.println(moisture);
    lora.send_temp_mois(SensorId,temperature,moisture);
  }
  digitalWrite(LED_BUILTIN, LOW);  
  delay(UpdatePeriod*1000);
}
