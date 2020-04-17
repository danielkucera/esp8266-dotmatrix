#include "LedMatrix.h"
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <WiFiManager.h>          //https://github.com/tzapu/WiFiManager WiFi Configuration Magic

WiFiUDP Udp;
WiFiManager wifiManager;
unsigned int localUdpPort = 1234;

#define NUMBER_OF_DEVICES 4
#define CS_PIN 4
#define HOSTNAME "esp-dotmatrix"
LedMatrix ledMatrix = LedMatrix(NUMBER_OF_DEVICES, CS_PIN);

void setup() {
  Serial.begin(115200); // For debugging output

  ledMatrix.init();
  ledMatrix.setIntensity(1); // range is 0-15
  ledMatrix.clear();
  ledMatrix.setTextAlignment(TEXT_ALIGN_LEFT);
  ledMatrix.setText("connecting ...");
  ledMatrix.drawText();
  ledMatrix.commit();

  //wifiManager.resetSettings();

  wifiManager.setConfigPortalTimeout(120);
  wifiManager.autoConnect(HOSTNAME);

  ArduinoOTA.begin();

  MDNS.setHostname(HOSTNAME);

  int lastOctet = WiFi.localIP()[3];

  ledMatrix.clear();
  ledMatrix.setTextAlignment(TEXT_ALIGN_LEFT);
  ledMatrix.setText(String(lastOctet));
  ledMatrix.drawText();
  ledMatrix.commit();

  Udp.begin(localUdpPort);
}

char incomingPacket[255];

void loop() {
  ArduinoOTA.handle();

  int packetSize = Udp.parsePacket();
  if (packetSize)
  {
    int len = Udp.read(incomingPacket, 255);
    if (len > 0)
    {
      ledMatrix.clear();
      for (int i=0; (i<8*NUMBER_OF_DEVICES) && (i<packetSize); i++){
        ledMatrix.setColumn(i, incomingPacket[i]);
        //ledMatrix.setColumn(i, 0xAA);
      }
      ledMatrix.commit(); // commit transfers the byte buffer to the displays
    }
  }
}
