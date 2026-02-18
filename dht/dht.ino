#include <WiFi.h>
#include <HTTPClient.h>
#include "time.h"
#include <dht_nonblocking.h>
#include "secret.h"

const char* ssid     = SECRET_SSID;
const char* password = SECRET_PASS;
const char* serverUrl = SECRET_URL;

const char* ntpServer = "pool.ntp.org";
#define DHT_SENSOR_TYPE DHT_TYPE_11
static const int DHT_SENSOR_PIN = 2; 
DHT_nonblocking dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

void setup() {
  Serial.begin(115200);
  delay(1000); 
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("Connecting to "); 
    Serial.println(ssid); 
  }
  Serial.println(" WiFi Connected");

  configTime(0, 0, ntpServer);
  delay(2000);
  float temperature, humidity;
  bool readSuccess = false;
  unsigned long startAttemptTime = millis(); 

  Serial.println("Waiting for sensor to be ready...");

  while (millis() - startAttemptTime < 60000) { 
    if (dht_sensor.measure(&temperature, &humidity)) {
      readSuccess = true;
      break; 
    }
    delay(200); 
    Serial.print(".");
  }
  if(readSuccess) {
    if(WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      struct tm timeinfo;
      if(getLocalTime(&timeinfo)){
        char timeStr[25];
        strftime(timeStr, sizeof(timeStr), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);

        String jsonPayload = "{";
        jsonPayload += "\"timestamp\":\"" + String(timeStr) + "\",";
        jsonPayload += "\"temperature\":" + String(temperature, 1) + ",";
        jsonPayload += "\"humidity\":" + String(humidity, 1) + ",";
        jsonPayload += "\"source\":\"HeltecV3_Sensor\"";
        jsonPayload += "}";

        Serial.println("Uploading: " + jsonPayload);
        int httpResponseCode = http.POST(jsonPayload);
        Serial.printf("HTTP Response code: %d\n", httpResponseCode);
        http.end();
      }
    }
  } else {
    Serial.println("Sensor read failed (Timeout). Please check your wiring!");
  }

  Serial.println("Going to sleep now for 30 minutes...");
  Serial.flush(); 
  esp_sleep_enable_timer_wakeup(30 * 60 * 1000000); 
  esp_deep_sleep_start();
}
void loop() {}