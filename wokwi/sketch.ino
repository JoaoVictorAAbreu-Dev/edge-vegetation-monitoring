#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "grupo5/esp32/temperatura";

#define DHT_PIN 15
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
unsigned long lastPublish = 0;

void connectWiFi() {
  Serial.print("Conectando ao Wokwi-GUEST");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" conectado");
}

void connectMQTT() {
  while (!mqtt.connected()) {
    String clientId = "WOKWI-GRUPO5-" + String((uint32_t)(ESP.getEfuseMac() & 0xFFFFFFFF), HEX);
    Serial.print("Conectando ao broker MQTT...");
    if (mqtt.connect(clientId.c_str())) {
      Serial.println(" conectado");
    } else {
      Serial.print(" falhou: ");
      Serial.println(mqtt.state());
      delay(2000);
    }
  }
}

void publishReading() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Leitura inválida do DHT22");
    return;
  }

  String payload = "{\"sensor\":\"temperatura_ambiente\",\"valor\":";
  payload += String(temperature, 2);
  payload += ",\"umidade\":";
  payload += String(humidity, 2);
  payload += ",\"unidade\":\"°C\",\"dispositivo\":\"ESP32-WOKWI-GRUPO5\",\"timestamp_ms\":";
  payload += String(millis());
  payload += "}";

  mqtt.publish(MQTT_TOPIC, payload.c_str());
  Serial.println(payload);
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWiFi();
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (!mqtt.connected()) connectMQTT();
  mqtt.loop();

  if (millis() - lastPublish >= 5000) {
    lastPublish = millis();
    publishReading();
  }
}
