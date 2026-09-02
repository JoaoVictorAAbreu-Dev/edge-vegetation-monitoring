"""Smoke test local do fluxo MQTT -> roteamento -> relatório."""

import json
from unittest.mock import patch

from src.mqtt_consumer import process_payload


def payload(value: float) -> bytes:
    return json.dumps({
        "sensor": "temperatura_ambiente",
        "valor": value,
        "unidade": "°C",
        "dispositivo": "ESP32-TESTE",
    }, ensure_ascii=False).encode("utf-8")


with patch("src.mqtt_consumer.generate_report", side_effect=lambda m: f"relatorio para {m['valor']} °C"):
    conform_report = process_payload(payload(24.0))
    alert_report = process_payload(payload(32.0))

assert conform_report.name.endswith("_conforme.md")
assert alert_report.name.endswith("_alerta.md")
print("SMOKE_TEST_OK")
print(conform_report)
print(alert_report)
