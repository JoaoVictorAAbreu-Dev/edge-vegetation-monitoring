"""Smoke test local do fluxo MQTT -> roteamento -> relatório."""

import json
from unittest.mock import patch

from app.mqtt_consumer import process_payload


def payload(value: float) -> bytes:
    # Monta uma mensagem igual à recebida pelo consumidor via MQTT.
    return json.dumps({
        "sensor": "temperatura_ambiente",
        "valor": value,
        "unidade": "°C",
        "dispositivo": "ESP32-TESTE",
    }, ensure_ascii=False).encode("utf-8")


# Substitui temporariamente a chamada ao LLM para testar apenas o roteamento.
with patch("app.mqtt_consumer.generate_report", side_effect=lambda m: f"relatorio para {m['valor']} °C"):
    # 24 °C deve ser encaminado à direção.
    conform_report = process_payload(payload(24.0))
    # 32 °C deve ser encaminado à equipe de sustentação.
    alert_report = process_payload(payload(32.0))

# Confirma que o consumidor classificou e nomeou os arquivos corretamente.
assert conform_report.name.endswith("_conforme.md")
assert alert_report.name.endswith("_alerta.md")
print("SMOKE_TEST_OK")
print(conform_report)
print(alert_report)
