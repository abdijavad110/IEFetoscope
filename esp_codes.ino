#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
//#include <HTTPClient.h>
#include <esp_task_wdt.h>


#define FILT_SIG_PIN 32
#define AUDIO_BUFFER_MAX 500

uint32_t seq_num = 0;
uint32_t bufferPointer = 0;
uint8_t audioBuffer[AUDIO_BUFFER_MAX*2+2];
uint8_t transmitBuffer[AUDIO_BUFFER_MAX*2+2];


const char* password = "*************";
const char* ssid     = "*************";
//const char* host     = "http://*************:8000/esp";
const char * udpAddress = "*************";
const int udpPort = 12000;

WiFiUDP udp;
bool transmitNow = false;
TaskHandle_t signalSampler;

void Sampler(void * parameter)
{
  int value;
  for( ;; )
  {
    value = analogRead(FILT_SIG_PIN);
    audioBuffer[2 * bufferPointer] = value>>8;
    audioBuffer[2 * bufferPointer++ + 1] = value % 256;

    if (bufferPointer == AUDIO_BUFFER_MAX) {
      audioBuffer[2 * bufferPointer] = seq_num++;
      bufferPointer = 0;
      memcpy(transmitBuffer, audioBuffer, (AUDIO_BUFFER_MAX + 1) * sizeof(uint16_t));
      transmitNow = true;
      esp_task_wdt_reset();
    }
    vTaskDelay(1);
  }
}


void setup(){
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  esp_task_wdt_init(5000, true);
  esp_task_wdt_add(NULL);

  xTaskCreatePinnedToCore(
    Sampler,
    "Sampler",
    1000,
    NULL,
    1,
    &signalSampler,
    0);
}

void loop(){
  if (transmitNow) {
    uint8_t start_flag[4] = {0, 0, 0, 0};
    uint8_t stop_flag[4] = {0x11, 0x11, 0x11, 0x11};
    transmitNow = false;
    if(WiFi.status()== WL_CONNECTED){
      udp.beginPacket(udpAddress, udpPort);
      udp.write(start_flag, 4);
      udp.write(transmitBuffer, (AUDIO_BUFFER_MAX + 1) * sizeof(uint16_t));
      udp.write(stop_flag, 4);
      udp.endPacket();
    }
  }
}
