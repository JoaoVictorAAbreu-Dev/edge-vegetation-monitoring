#include <WiFi.h>
#include <PubSubClient.h>
#include <Arduino.h>

bool mqttStatus = 0;

const char* ssid = "sua_rede_aqui"; // REDE WIFi
const char* password = "senha_da_sua_rede"; // SENHA WIFi

// MQTT Broker
const char *mqtt_broker = "broker.hivemq.com";//Host do broket
const char* topic[] = {
  "topico01",
  "topico02",
  "topico03"
};//Topico a ser subscrito e publicado
const char *mqtt_username = "";            //Usuario (se houver)
const char *mqtt_password = "";            //Senha (se houver)
const int mqtt_port = 1883;                //Porta
int totalTopicos = sizeof(topic) / sizeof(topic[0]);

String mensagem;

//Objetos
WiFiClient espClient;
PubSubClient client(espClient);

//Prototipos
bool connectMQTT();
void callback(char *topic, byte * payload, unsigned int length);

void setup(void){
  Serial.begin(9600);

  // Conectar
  WiFi.begin(ssid, password);

  //Aguardando conexão
  Serial.println();
  Serial.print("Conectando");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  //Envia IP através da UART
  Serial.println(WiFi.localIP());

  mqttStatus =  connectMQTT();
}

void loop() {
 static long long pooling  = 0;
  if (mqttStatus){

    client.loop();

    if (millis() > pooling +1000){
      pooling = millis();



    //Inclua aqui a sua lógica
      String msg = mensagem; //recebe uma mensagem
      client.publish(topic[0], msg.c_str()); //envia uma mensagem



    }
  }
}






bool connectMQTT() {
  byte tentativa = 0;
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);

  do {
    String client_id = "BOBSIEN-";
    client_id += String(WiFi.macAddress());

    if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("Exito na conexão:");
      Serial.printf("Cliente %s conectado ao broker\n", client_id.c_str());
    } else {
      Serial.print("Falha ao conectar: ");
      Serial.print(client.state());
      Serial.println();
      Serial.print("Tentativa: ");
      Serial.println(tentativa);
      delay(2000);
    }
    tentativa++;
  } while (!client.connected() && tentativa < 5);

  if (tentativa < 5) {
    // publish and subscribe
    client.publish(topic[0], "{testeOK}");
    for(int i=0; i<totalTopicos; i++){
      client.subscribe(topic[i]);
    }
    return 1;
  } else {
    Serial.println("Não conectado");
    return 0;
  }
}

void callback(char *topic, byte * payload, unsigned int length) {
  mensagem = "";
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial.print((char) payload[i]);
    mensagem += (char)payload[i];
  }
  Serial.println();
  Serial.println("-----------------------");
}
