#include <Arduino.h>
#include <SPI.h>
#include "LedMatrix.h"
#include <NTPClient.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

const char *ssid     = "coloseum";
const char *password = "Kucerovisu1";

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 7200, 60000);

#define NUMBER_OF_DEVICES 4
#define CS_PIN 4
LedMatrix ledMatrix = LedMatrix(NUMBER_OF_DEVICES, CS_PIN);

void setup() {
  Serial.begin(115200); // For debugging output

  WiFi.begin(ssid, password);

  ledMatrix.init();
  ledMatrix.setIntensity(1); // range is 0-15
  ledMatrix.clear();
  ledMatrix.setTextAlignment(TEXT_ALIGN_LEFT);
  ledMatrix.setText("connecting ...");
  ledMatrix.drawText();
  ledMatrix.commit();

  while ( WiFi.status() != WL_CONNECTED ) {
    delay ( 500 );
  }

  timeClient.begin();
}

char text[10];

void loop() {
  timeClient.update();
  ledMatrix.clear();

  sprintf(text, "%2d%2d" , timeClient.getHours(), timeClient.getMinutes());

  ledMatrix.setTextAlignment(TEXT_ALIGN_LEFT);
  ledMatrix.setText(text);
  ledMatrix.drawText();

/*
  ledMatrix.setTextAlignment(TEXT_ALIGN_LEFT);
  ledMatrix.setText(String(timeClient.getHours()));
  ledMatrix.drawText();

  ledMatrix.setTextAlignment(TEXT_ALIGN_RIGHT);
  ledMatrix.setText(":");
  ledMatrix.drawText();

  ledMatrix.setTextAlignment(TEXT_ALIGN_RIGHT);
  ledMatrix.setText(String(timeClient.getMinutes()));
  ledMatrix.drawText();
*/

  ledMatrix.commit(); // commit transfers the byte buffer to the displays
  delay(1000);
}
