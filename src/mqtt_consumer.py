"""Consumidor MQTT que dispara a CrewAI a cada telemetria válida."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt

from .config import (
    MQTT_BROKER,
    MQTT_CLIENT_ID,
    MQTT_PORT,
    MQTT_TOPIC,
    REPORTS_DIR,
    TEMPERATURE_MAX_C,
    TEMPERATURE_MIN_C,
)
from .crew_agents import generate_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
LOGGER = logging.getLogger("grupo5-mqtt")


def normalize_message(payload: bytes) -> dict:
    """Valida e padroniza o payload JSON publicado pelo ESP32."""
    data = json.loads(payload.decode("utf-8"))
    required = {"sensor", "valor", "unidade", "dispositivo"}
    missing = required.difference(data)
    if missing:
        raise ValueError(f"Campos ausentes: {', '.join(sorted(missing))}")

    valor = float(data["valor"])
    if not -1000 < valor < 1000:
        raise ValueError("Valor do sensor fora do domínio aceitável para a simulação")

    return {
        "sensor": str(data["sensor"]),
        "valor": valor,
        "unidade": str(data["unidade"]),
        "dispositivo": str(data["dispositivo"]),
        "timestamp": str(data.get("timestamp", datetime.now(timezone.utc).isoformat())),
        "topico": MQTT_TOPIC,
        "status": "DENTRO" if TEMPERATURE_MIN_C <= valor <= TEMPERATURE_MAX_C else "FORA",
        "destinatario": "direção" if TEMPERATURE_MIN_C <= valor <= TEMPERATURE_MAX_C else "equipe de sustentação",
    }


def save_report(report: str, measurement: dict) -> Path:
    """Salva o relatório com status e timestamp no nome do arquivo."""
    status = "conforme" if measurement["status"] == "DENTRO" else "alerta"
    destinatario = measurement["destinatario"]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = REPORTS_DIR / f"{stamp}_{status}.md"
    path.write_text(
        "# Grupo 5 — Relatório de Telemetria MQTT\n\n"
        f"**Status automático:** {measurement['status']}  \n"
        f"**Destinatário:** {destinatario}  \n"
        f"**Faixa configurada:** {TEMPERATURE_MIN_C} °C a {TEMPERATURE_MAX_C} °C  \n\n"
        + report,
        encoding="utf-8",
    )
    return path


def process_payload(payload: bytes) -> Path:
    """Processa um payload sem depender de uma conexão MQTT ativa; útil para testes."""
    measurement = normalize_message(payload)
    LOGGER.info("Leitura recebida: %s", measurement)
    report = generate_report(measurement)
    path = save_report(report, measurement)
    LOGGER.info("Relatório salvo em %s", path)
    return path


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        LOGGER.info("Conectado ao broker %s:%s", MQTT_BROKER, MQTT_PORT)
        client.subscribe(MQTT_TOPIC)
        LOGGER.info("Inscrito no tópico %s", MQTT_TOPIC)
    else:
        LOGGER.error("Falha na conexão MQTT: %s", reason_code)


def on_message(client, userdata, message):
    try:
        process_payload(message.payload)
    except (ValueError, json.JSONDecodeError) as exc:
        LOGGER.warning("Payload ignorado: %s", exc)
    except Exception:
        LOGGER.exception("Falha ao gerar relatório")


def run_consumer() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    LOGGER.info("Aguardando mensagens MQTT. Pressione Ctrl+C para encerrar.")
    client.loop_forever()
