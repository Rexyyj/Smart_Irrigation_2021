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
    byte dataArray[13] = {
        id,
        0x00,
        0x01,
      ((uint8_t*)&temperature)[0],
      ((uint8_t*)&temperature)[1],
      ((uint8_t*)&temperature)[2],
      ((uint8_t*)&temperature)[3],
        0x00,
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

bool LoRaCom::send_multi_layer(uint8_t id,float tmp1, float tmp2,float tmp3,float moi1, float moi2, float moi3){
    int err;
    byte dataArray[29] = {
        id,
        0x00,
        0x11,
      ((uint8_t*)&tmp1)[0],
      ((uint8_t*)&tmp1)[1],
      ((uint8_t*)&tmp1)[2],
      ((uint8_t*)&tmp1)[3],
      ((uint8_t*)&tmp2)[0],
      ((uint8_t*)&tmp2)[1],
      ((uint8_t*)&tmp2)[2],
      ((uint8_t*)&tmp2)[3],
      ((uint8_t*)&tmp3)[0],
      ((uint8_t*)&tmp3)[1],
      ((uint8_t*)&tmp3)[2],
      ((uint8_t*)&tmp3)[3],
        0x00,
        0x12,
      ((uint8_t*)&moi1)[0],
      ((uint8_t*)&moi1)[1],
      ((uint8_t*)&moi1)[2],
      ((uint8_t*)&moi1)[3],
      ((uint8_t*)&moi2)[0],
      ((uint8_t*)&moi2)[1],
      ((uint8_t*)&moi2)[2],
      ((uint8_t*)&moi2)[3],
      ((uint8_t*)&moi3)[0],
      ((uint8_t*)&moi3)[1],
      ((uint8_t*)&moi3)[2],
      ((uint8_t*)&moi3)[3],
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

