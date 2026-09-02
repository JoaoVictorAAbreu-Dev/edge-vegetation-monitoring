"""Configurações da aplicação do Grupo 5."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "grupo5/esp32/temperatura")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "grupo5-crewai-consumer")

# Sensor mockado: temperatura ambiente de uma sala de equipamentos.
TEMPERATURE_MIN_C = float(os.getenv("TEMPERATURE_MIN_C", "18"))
TEMPERATURE_MAX_C = float(os.getenv("TEMPERATURE_MAX_C", "27"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
