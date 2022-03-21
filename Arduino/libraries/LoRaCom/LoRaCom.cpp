#include "LoRaCom.h"

LoRaCom::LoRaCom(String appEui,String appKey)
{
    _appKey = appKey;
    _appEui = appEui;

}
bool type_c_flag=false;
void LoRaCom::connect(){
        // Set up frequency band
    if (!_modem.begin(EU868)) {
        status= false; 
        errorMsg="Frequency band setting error";
        return;
    }
    // check modem framework version
    if(_modem.version()!=ARDUINO_FW_VERSION){
        status=false;
        errorMsg="modem framework error";
    }
    
    _deviceEui = _modem.deviceEUI();
    
    if (type_c_flag==true){
         _modem.configureClass(CLASS_C);
    }

    _appEui.trim();
    _appKey.trim();
    // Serial.println(_appEui);
    // Serial.println(_appKey);

    if (!_modem.joinOTAA(_appEui, _appKey)){
        status = false;
        errorMsg="Connection error";
    }else{
        status = true;
        _modem.setPort(3);
    }
}

void LoRaCom::change_to_class_C(){
   type_c_flag=true;
}


String LoRaCom::get_device_eui(){
    return _deviceEui;
}

bool LoRaCom::send(String data){
    int err;
    if (status == true){
        _modem.beginPacket();
        _modem.print(data);
        err = _modem.endPacket(true);
        if (err >0){
            return true;
        }else{
            return false;
        }
    }else{
        return false;
    }
}

bool LoRaCom::send(float data){
    int err;
    byte dataArray[4] = {
      ((uint8_t*)&data)[0],
      ((uint8_t*)&data)[1],
      ((uint8_t*)&data)[2],
      ((uint8_t*)&data)[3]
   };

    if (status == true){
        _modem.beginPacket();
        _modem.write(dataArray,sizeof(dataArray));
        err = _modem.endPacket(true);
        if (err >0){
            return true;
        }else{
            return false;
        }
    }else{
        return false;
    }
}

bool LoRaCom::send_temp_mois(uint8_t id, float temperature, float mosisture){
    int err;
    byte dataArray[12] = {
        id,
        0x00,
        0x01,
      ((uint8_t*)&temperature)[0],
      ((uint8_t*)&temperature)[1],
      ((uint8_t*)&temperature)[2],
      ((uint8_t*)&temperature)[3],
        0x02,
      ((uint8_t*)&mosisture)[0],
      ((uint8_t*)&mosisture)[1],
      ((uint8_t*)&mosisture)[2],
      ((uint8_t*)&mosisture)[3]
   };

    if (status == true){
        _modem.beginPacket();
        _modem.write(dataArray,sizeof(dataArray));
        err = _modem.endPacket(true);
        if (err >0){
            return true;
        }else{
            return false;
        }
    }else{
        return false;
    }
}

bool LoRaCom::send_pump_status(uint8_t id, char state){
    int err;
    byte dataArray[4] = {
        id,
        0x01,
        0x01,
        state
   };

    if (status == true){
        _modem.beginPacket();
        _modem.write(dataArray,sizeof(dataArray));
        err = _modem.endPacket(true);
        if (err >0){
            return true;
        }else{
            return false;
        }
    }else{
        return false;
    }
}


int LoRaCom::get_receive(){
    if (!_modem.available()) {
    return -1;
    }
    else{
    char rcv[64] = "";
    int i = 0;
    while (_modem.available()) {
      rcv[i % 64] = (char)_modem.read();
      ++i;
    }

    String messagio = rcv;
    return messagio.toInt();
  }
}

