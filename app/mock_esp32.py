"""Simulador do ESP32 e de um sensor de temperatura."""

import argparse
import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.publish as publish

from .config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC


def build_reading(mode: str) -> dict:
    # Gera uma temperatura dentro ou fora da faixa para simular o sensor.
    if mode == "normal":
        value = round(random.uniform(20, 25), 2)
    elif mode == "alerta":
        value = round(random.choice([random.uniform(10, 17), random.uniform(28, 38)]), 2)
    else:
        value = round(random.uniform(10, 38), 2)

    # O formato do dicionário é o mesmo que o ESP32 publica via MQTT.
    return {
        "sensor": "temperatura_ambiente",
        "valor": value,
        "unidade": "°C",
        "dispositivo": "ESP32-GRUPO5",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    # Permite demonstrar a aplicação sem precisar de uma placa física.
    parser = argparse.ArgumentParser(description="Publica dados mockados do ESP32 via MQTT")
    parser.add_argument("--modo", choices=["normal", "alerta", "aleatorio"], default="normal")
    parser.add_argument("--quantidade", type=int, default=1)
    parser.add_argument("--intervalo", type=float, default=2.0)
    args = parser.parse_args()

    # Publica uma ou mais leituras no tópico configurado.
    for index in range(args.quantidade):
        reading = build_reading(args.modo)
        payload = json.dumps(reading, ensure_ascii=False)
        publish.single(MQTT_TOPIC, payload=payload, hostname=MQTT_BROKER, port=MQTT_PORT)
        print(f"Publicado em {MQTT_TOPIC}: {payload}")
        if index + 1 < args.quantidade:
            time.sleep(args.intervalo)


if __name__ == "__main__":
    main()
