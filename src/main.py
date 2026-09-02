"""Ponto de entrada da aplicação do Grupo 5."""

import argparse
import json

from .mqtt_consumer import process_payload, run_consumer


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor IoT com CrewAI e MQTT")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ouvir", help="Escuta o tópico MQTT continuamente")
    teste = subparsers.add_parser("teste", help="Processa uma leitura local")
    teste.add_argument("--valor", type=float, required=True, help="Temperatura em °C")

    args = parser.parse_args()
    if args.command == "ouvir":
        run_consumer()
    else:
        payload = {
            "sensor": "temperatura_ambiente",
            "valor": args.valor,
            "unidade": "°C",
            "dispositivo": "ESP32-GRUPO5-TESTE",
        }
        path = process_payload(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        print(f"Relatório gerado: {path}")


if __name__ == "__main__":
    main()
