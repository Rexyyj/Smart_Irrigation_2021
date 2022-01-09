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
        void connect();
        bool send(String data);
        bool send(float data);
        bool send_temp_mois(uint8_t id, float temperature, float mosisture);
        String receive(String data);
        String get_device_eui();
    private:
        LoRaModem _modem;
        String _deviceEui;
        String _appEui;
        String _appKey;
};




#endif
