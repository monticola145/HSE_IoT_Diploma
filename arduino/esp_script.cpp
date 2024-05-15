#include <ESP8266HTTPClient.h>  
#include <ESP8266WiFi.h>  
#include <SoftwareSerial.h>  
 
#define SERVER_IP "http://server_ip:5000/update"   
 
#ifndef STASSID  
#define STASSID "name"  
#define STAPSK "password"  
const char* BToken = "token";   
#endif  
 
const char* ssid = STASSID;  
const char* password = STAPSK;  
 
void setup() {  
  Serial.begin(115200);  
  Serial.println("\n\nConnecting to ");  
  Serial.println(ssid);  
 
  WiFi.mode(WIFI_STA); 
  WiFi.begin(ssid, password);  
 
  while (WiFi.status() != WL_CONNECTED) {  
    delay(500);  
    Serial.print(".");  
  }  
 
  Serial.println("\nWiFi connected");  
  Serial.println("IP address: ");  
  Serial.println(WiFi.localIP());  
}  
 
void loop() {  
  if (WiFi.status() == WL_CONNECTED && Serial.available() > 0) {  
    String lightString = Serial.readStringUntil('\n');   
 
    WiFiClient client;  
    HTTPClient http;  
 
    http.begin(client, SERVER_IP);  
    http.addHeader("Authorization", "Bearer " + String(BToken)); 
    http.addHeader("Content-Type", "application/json");  
 
    String jsonData = "{\"data\": \"" + lightString.substring(0, lightString.length() - 1) + "\"}";  // JSON data 
 
    int httpCode = http.POST(jsonData);  
    String payload = http.getString(); 
 
    if (httpCode > 0) {  
      Serial.printf("[HTTP] POST... code: %d\n", httpCode);  
      if (httpCode == HTTP_CODE_OK) {  
        Serial.println("Received payload:\n<<" + payload + ">>");  
      } 
    } else {  
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str()); 
    } 
 
    http.end();  
  } 
   
  delay(10000); 
}
