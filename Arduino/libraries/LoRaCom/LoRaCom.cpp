#include "LoRaCom.h"

LoRaCom::LoRaCom(String appEui,String appKey)
{
    _appKey = appKey;
    _appEui = appEui;

}

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
    

    // _appEui.trim();
    // _appKey.trim();
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


String LoRaCom::get_device_eui(){
    return _deviceEui;
}

String LoRaCom::send(String data){
    int err;
    if (status == true){
        _modem.beginPacket();
        _modem.print(data);
        err = _modem.endPacket(true);
        if (err >0){
            return "success";
        }else{
            return "send error";
        }
    }else{
        return "status error";
    }
}

String LoRaCom::receive(String data){
    return "";
}

