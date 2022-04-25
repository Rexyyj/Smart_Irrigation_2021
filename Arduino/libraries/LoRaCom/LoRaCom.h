#ifndef __LoRaCom__
#define __LoRaCom__

#include "Arduino.h"
#include <MKRWAN.h>

class LoRaCom
{
    public:
        bool status;
        String errorMsg;
        int connection;

        LoRaCom(String appEui,String appKey);
        void change_to_class_C();
        void connect();
        bool send(String data);
        bool send(float data);
        bool send_temp_mois(uint8_t id, float temperature, float mosisture);
        bool send_pump_status(uint8_t id, char state);
        bool send_multi_layer(uint8_t id,float tmp1, float tmp2,float tmp3,float moi1, float moi2, float moi3);
        int get_receive();
        String get_device_eui();
    private:
        LoRaModem _modem;
        String _deviceEui;
        String _appEui;
        String _appKey;
};




#endif
