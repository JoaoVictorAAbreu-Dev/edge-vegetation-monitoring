# Grupo 5 — Monitor de Sensor ESP32 com MQTT e CrewAI

## Objetivo

Esta aplicação recebe uma leitura de temperatura mockada de um ESP32 por MQTT, analisa a conformidade da leitura com uma faixa de operação e gera um relatório executivo em Markdown para a direção. O projeto implementa o padrão apresentado na aula: **Agentes**, **Tasks**, **Crew** e processo sequencial.

O sensor escolhido é o de **temperatura ambiente de uma sala de equipamentos**. Para a demonstração, a faixa considerada adequada é de **18 °C a 27 °C**, inclusive. Esses valores são parâmetros e podem ser alterados no arquivo `.env`.

## Arquitetura

```text
ESP32 real ou mockado
        |
        | publica JSON via MQTT
        v
broker.hivemq.com:1883
        |
        | tópico: grupo5/esp32/temperatura
        v
Consumidor Python
        |
        | valida e normaliza a mensagem
        v
CrewAI — processo sequencial
  1. Analista de telemetria IoT
  2. Redator de relatórios para a direção
        |
        v
reports/YYYYMMDD_HHMMSS_status.md
```

O sketch enviado pela equipe já utiliza o broker público `broker.hivemq.com`, a porta `1883` e uma lista de tópicos. Para evitar o uso de `topico01` compartilhado por outras pessoas, este projeto usa o tópico `grupo5/esp32/temperatura`. Se o ESP32 continuar publicando em `topico01`, basta definir `MQTT_TOPIC=topico01` no `.env` e publicar o JSON no formato indicado abaixo.

## Formato da mensagem

```json
{
  "sensor": "temperatura_ambiente",
  "valor": 24.5,
  "unidade": "°C",
  "dispositivo": "ESP32-GRUPO5",
  "timestamp": "2026-08-27T12:00:00+00:00"
}
```

Quando `valor` estiver entre 18 e 27, o relatório deve destacar a conformidade e os impactos positivos: estabilidade do ambiente, menor risco operacional relacionado à temperatura e apoio à continuidade da operação. Quando `valor` estiver abaixo de 18 ou acima de 27, o relatório deve ser de alerta, com risco potencial, prioridade e ações corretivas sugeridas.

## Instalação

Recomenda-se Python 3.10 ou superior. No terminal, execute:

```bash
cd grupo5-crewai-mqtt
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
```

Depois, abra `.env` e informe uma chave válida de LLM em `OPENAI_API_KEY`. A CrewAI usa o modelo configurado em `OPENAI_MODEL`; o padrão do projeto é `gpt-4o-mini`.

## Execução com MQTT

Abra dois terminais, mantendo o ambiente virtual ativado.

No primeiro, inicie o consumidor:

```bash
python -m src.main ouvir
```

No segundo, publique uma leitura normal:

```bash
python -m src.mock_esp32 --modo normal --quantidade 1
```

Para simular um problema:

```bash
python -m src.mock_esp32 --modo alerta --quantidade 1
```

O relatório aparecerá na pasta `reports/`. O arquivo termina em `_conforme.md` ou `_alerta.md`, facilitando a demonstração do encaminhamento lógico para a direção.

## Teste local sem depender do MQTT

A aplicação também oferece um modo de teste que percorre a validação e a CrewAI sem precisar publicar no broker:

```bash
python -m src.main teste --valor 24
python -m src.main teste --valor 32
```

O primeiro comando representa o cenário correto; o segundo representa o cenário fora da especificação.

## Adaptação do sketch do ESP32

No arquivo `MQTT_ESP.ino`, mantenha as credenciais Wi-Fi e o broker. A lógica de publicação pode ser substituída por:

```cpp
String msg = "{\"sensor\":\"temperatura_ambiente\",\"valor\":24.5,\"unidade\":\"°C\",\"dispositivo\":\"ESP32-GRUPO5\"}";
client.publish("grupo5/esp32/temperatura", msg.c_str());
```

Em um projeto real, o valor fixo deve ser substituído pela leitura do sensor conectado ao ESP32. Para uma apresentação, o simulador Python já atende ao requisito de sensor mockado.

## Divisão sugerida para a apresentação

| Parte | Responsabilidade | Evidência |
|---|---|---|
| ESP32/MQTT | Explicar broker, tópico e payload | Sketch e terminal de publicação |
| Integração | Mostrar o consumidor recebendo a mensagem | Log de conexão e leitura |
| Agentes | Explicar analista, redator, tasks e Crew sequencial | `app/crew_agents.py` |
| Regra de negócio | Demonstrar faixa 18–27 °C | `.env` e relatório |
| Resultado | Comparar relatório conforme e relatório de alerta | Pasta `reports/` |

## Observações de segurança e operação

O broker público é adequado para uma demonstração acadêmica, mas não deve ser usado para dados sensíveis ou produção. Em ambiente real, use broker privado, autenticação, TLS e tópicos próprios. Também é importante evitar credenciais no código e nunca versionar o arquivo `.env`.

## Versão para testar no Wokwi

A pasta `simulation/wokwi/` contém os três arquivos necessários para a simulação: `sketch.ino`, `diagram.json` e `libraries.txt`. O circuito possui um ESP32 DevKit e um DHT22 simulado conectado ao GPIO 15.

Para testar, crie um novo projeto de **ESP32 no Wokwi**, substitua o conteúdo do sketch pelo arquivo `simulation/wokwi/sketch.ino`, substitua o diagrama pelo arquivo `simulation/wokwi/diagram.json` e adicione as bibliotecas listadas em `simulation/wokwi/libraries.txt`. Inicie a simulação e abra o monitor serial. O ESP32 usará a rede virtual `Wokwi-GUEST`, conectará ao broker MQTT e publicará a cada cinco segundos.

O valor do DHT22 pode ser alterado clicando no componente durante a simulação. Para o cenário conforme, utilize uma temperatura entre **18 °C e 27 °C**, como 24 °C. Para o cenário de alerta, utilize uma temperatura acima de 27 °C, como 32 °C, ou abaixo de 18 °C, como 15 °C. Com o consumidor Python rodando em outro terminal, cada publicação produzirá um relatório na pasta `reports/`.

O broker público pode não permitir conexões dependendo das restrições de rede do navegador ou da simulação. Caso isso ocorra, a equipe ainda pode demonstrar o circuito e o payload no monitor serial e usar o simulador Python local para validar a geração dos relatórios:

```bash
python -m src.main teste --valor 24
python -m src.main teste --valor 32
```

## Arquivos de código do ESP32

O arquivo `hardware/esp32/MQTT_ESP_COMPLETO.ino` é a versão para uma placa real. Ele usa as credenciais Wi-Fi informadas no início do arquivo, o mesmo broker e o mesmo tópico do consumidor Python. O arquivo `MQTT_ESP_original.ino` é uma cópia do sketch enviado pela equipe, preservada para comparação.

## Atendimento exato ao checkpoint

A regra de negócio implementada corresponde ao enunciado da atividade:

| Resultado da leitura | Destinatário | Conteúdo do relatório |
|---|---|---|
| Fora da especificação, abaixo de 18 °C ou acima de 27 °C | Equipe de sustentação | Desvio identificado, risco operacional, prioridade, ações imediatas e investigação recomendada |
| Dentro da especificação, entre 18 °C e 27 °C | Direção | Confirmação da conformidade, impactos positivos, continuidade da operação e recomendação executiva |

O status e o destinatário são calculados deterministicamente pelo consumidor MQTT antes da chamada ao agente. Dessa forma, o LLM redige o relatório, mas não pode alterar a regra fundamental de encaminhamento.

## Integração com a API do ChatGPT

A CrewAI utiliza o provedor OpenAI por meio das variáveis de ambiente. A chave não deve ser colocada em nenhum arquivo versionado, no código do ESP32 ou no README. Copie `.env.example` para `.env` e preencha:

```env
OPENAI_API_KEY=sua_chave_nova_aqui
OPENAI_MODEL=gpt-4o-mini
```

Depois, execute o consumidor com o ambiente virtual ativado. A aplicação carregará automaticamente o `.env` por meio de `python-dotenv`, e os agentes CrewAI usarão o modelo configurado para analisar a leitura e redigir o relatório.

> **Segurança:** a chave enviada na conversa ficou exposta e deve ser revogada no painel da OpenAI. Gere uma nova chave e coloque-a somente no arquivo `.env`, que já está protegido pelo `.gitignore`. Nunca faça commit, upload ou publicação de uma chave de API.

## Estrutura do projeto

| Diretório/arquivo | Descrição |
|---|---|
| `app/config.py` | Broker, tópico, limites e carregamento das variáveis de ambiente |
| `app/mqtt_consumer.py` | Recepção, validação, classificação e gravação dos relatórios |
| `app/crew_agents.py` | Agentes, tarefas e Crew sequencial |
| `app/mock_esp32.py` | Gerador de leituras normais ou em alerta |
| `hardware/esp32/` | Sketch para ESP32 real com DHT22 |
| `simulation/wokwi/` | Sketch, diagrama e bibliotecas para simulação no Wokwi |
| `reports/` | Relatórios gerados pela aplicação |
| `tests/test_smoke.py` | Teste do roteamento sem consumir a API |

## Execução com Docker

Docker empacota a aplicação e suas dependências em uma imagem reproduzível. Assim, em outro computador, basta instalar Docker Desktop ou Docker Engine, copiar o projeto e configurar a chave no arquivo `.env`.

### 1. Configurar as variáveis de ambiente

Na raiz do projeto, crie o arquivo `.env` a partir do modelo:

```bash
cp .env.example .env
```

Edite o arquivo e informe uma nova chave da API:

```env
OPENAI_API_KEY=sua_chave_nova_aqui
OPENAI_MODEL=gpt-4o-mini
```

Nunca publique o `.env` no GitHub. Ele já está protegido pelo `.gitignore` e pelo `.dockerignore`.

### 2. Iniciar o consumidor MQTT

Com Docker Compose:

```bash
docker compose up --build -d consumidor
```

O container ficará escutando o tópico MQTT e reiniciará automaticamente caso seja encerrado. Os relatórios continuam disponíveis na pasta local `reports/` por meio do volume configurado no `docker-compose.yml`.

Para visualizar os logs:

```bash
docker compose logs -f consumidor
```

Para encerrar:

```bash
docker compose down
```

### 3. Publicar uma leitura de teste

Com o consumidor em execução, use o mesmo container para publicar uma leitura normal:

```bash
docker compose run --rm consumidor python -m app.mock_esp32 --modo normal --quantidade 1
```

Para simular uma temperatura fora da especificação:

```bash
docker compose run --rm consumidor python -m app.mock_esp32 --modo alerta --quantidade 1
```

Também é possível executar um teste local diretamente no container:

```bash
docker compose run --rm consumidor python -m app.main teste --valor 24
docker compose run --rm consumidor python -m app.main teste --valor 32
```

### Execução sem Compose

Caso a equipe prefira usar apenas Docker:

```bash
docker build -t grupo5-edge-computing .
docker run --rm --env-file .env -v "$(pwd)/reports:/app/reports" grupo5-edge-computing
```

### Organização final

```text
checkpoint04-de-edge-computing/
├── app/                         # Aplicação Python e agentes CrewAI
├── hardware/esp32/              # Código para ESP32 real
├── simulation/wokwi/            # Sketch e circuito do Wokwi
├── tests/                       # Testes automatizados
├── reports/examples/            # Exemplos versionados de relatórios
├── Dockerfile                   # Imagem da aplicação
├── docker-compose.yml            # Execução simplificada do consumidor
├── .dockerignore                # Arquivos excluídos da imagem
├── requirements.txt             # Dependências Python
└── README.md                    # Documentação do projeto
```
