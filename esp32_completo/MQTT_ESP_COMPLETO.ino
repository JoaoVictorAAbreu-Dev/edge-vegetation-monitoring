#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// =========================
// CONFIGURAÇÕES DO PROJETO
// =========================
const char* WIFI_SSID = "SUA_REDE_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";

// Broker público usado apenas para demonstração acadêmica.
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "grupo5/esp32/temperatura";

// DHT22 conectado ao GPIO 15.
#define DHT_PIN 15
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

WiFiClient espClient;
PubSubClient mqttClient(espClient);
unsigned long ultimaPublicacao = 0;
const unsigned long INTERVALO_MS = 5000;

void conectarWiFi() {
  Serial.print("Conectando ao Wi-Fi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void conectarMQTT() {
  while (!mqttClient.connected()) {
    String clientId = "ESP32-GRUPO5-" + String((uint32_t)(ESP.getEfuseMac() & 0xFFFFFFFF), HEX);
    Serial.print("Conectando ao MQTT...");

    if (mqttClient.connect(clientId.c_str())) {
      Serial.println(" conectado");
    } else {
      Serial.print(" falhou, código=");
      Serial.print(mqttClient.state());
      Serial.println("; nova tentativa em 2 segundos");
      delay(2000);
    }
  }
}

void publicarTemperatura() {
  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();

  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("Falha na leitura do DHT22");
    return;
  }

  String payload = "{";
  payload += "\"sensor\":\"temperatura_ambiente\",";
  payload += "\"valor\":" + String(temperatura, 2) + ",";
  payload += "\"umidade\":" + String(umidade, 2) + ",";
  payload += "\"unidade\":\"°C\",";
  payload += "\"dispositivo\":\"ESP32-GRUPO5\",";
  payload += "\"timestamp_ms\":" + String(millis());
  payload += "}";

  if (mqttClient.publish(MQTT_TOPIC, payload.c_str())) {
    Serial.print("Publicado em ");
    Serial.print(MQTT_TOPIC);
    Serial.print(": ");
    Serial.println(payload);
  } else {
    Serial.println("Falha ao publicar a mensagem MQTT");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  dht.begin();
  conectarWiFi();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
  }

  if (!mqttClient.connected()) {
    conectarMQTT();
  }

  mqttClient.loop();

  if (millis() - ultimaPublicacao >= INTERVALO_MS) {
    ultimaPublicacao = millis();
    publicarTemperatura();
  }
}
