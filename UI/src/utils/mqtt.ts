import * as mqtt from 'mqtt';
import { MqttClient } from 'mqtt';

let client: MqttClient | null = null;

export const mqttInit = (force = false) => {
  if (client && !force) {
    return;
  }
  client = mqtt.connect({
    hostname: 'eu1.cloud.thethings.network',
    port: 1883,
    protocol: 'ws',
    username: 'hk-mqtt-test@ttn',
    password: 'JOHSZVY5JZVTMW2U4WI3DDFSF3I6XSZI3OHYOVI',
  });
  if (!client) {
    return;
  }

  client.on('connect', () => {
    client!.subscribe('v3/arduino-lora-test-rex/devices/A8610A32371B8001/down/push',  (err: any, granted) => {
      if (!err) {
        console.log('granted:', granted);
      }
    });
  });

  client.on('message', (topic: string, message: string) => {
    // message is Buffer
    console.log(message.toString());
    client!.end();
  });
};


export const publishMessage = (msg: string) => {
  if(!client) {
    console.log('client not connect server');
    return;
  }
  client.publish('v3/arduino-lora-test-rex/devices/A8610A32371B8001/down/push', msg);
};