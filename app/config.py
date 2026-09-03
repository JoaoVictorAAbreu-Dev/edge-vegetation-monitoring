"""Configurações da aplicação do Grupo 5."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega as configurações salvas no arquivo .env, quando ele existir.
load_dotenv()

# Diretório raiz do projeto e pasta onde os relatórios serão armazenados.
BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Parâmetros de conexão usados pelo consumidor MQTT.
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "grupo5/esp32/temperatura")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "grupo5-crewai-consumer")

# Sensor mockado: temperatura ambiente de uma sala de equipamentos.
# As leituras dentro desta faixa são consideradas conformes.
TEMPERATURE_MIN_C = float(os.getenv("TEMPERATURE_MIN_C", "18"))
TEMPERATURE_MAX_C = float(os.getenv("TEMPERATURE_MAX_C", "27"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
