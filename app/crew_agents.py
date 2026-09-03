"""Definição dos agentes e tarefas CrewAI do Grupo 5."""

from crewai import Agent, Crew, Process, Task

from .config import TEMPERATURE_MAX_C, TEMPERATURE_MIN_C


def build_crew() -> Crew:
    """Monta uma equipe sequencial para cada leitura recebida via MQTT."""
    # Este agente interpreta os dados e verifica se estão dentro da especificação.
    analista = Agent(
        role="Analista de telemetria IoT",
        goal=(
            "Interpretar a leitura de temperatura recebida do ESP32, comparar "
            "com a especificação e identificar riscos ou conformidade."
        ),
        backstory=(
            "Você é um analista sênior de IoT e operações. Trabalha com dados "
            "de sensores, conhece monitoramento ambiental e comunica achados "
            "de forma objetiva para gestores."
        ),
        verbose=True,
        allow_delegation=False,
    )

    # Este agente transforma a análise técnica em um relatório executivo.
    redator = Agent(
        role="Redator de relatórios para a direção",
        goal=(
            "Transformar a análise da telemetria em um relatório executivo "
            "claro e encaminhado ao destinatário correto: sustentação em caso "
            "de dado fora da especificação ou direção em caso de conformidade."
        ),
        backstory=(
            "Você é especialista em comunicação executiva. Quando há desvio, "
            "prioriza riscos, causas prováveis e ações corretivas. Quando os "
            "dados estão corretos, evidencia impactos positivos e ganhos para "
            "a operação."
        ),
        verbose=True,
        allow_delegation=False,
    )

    # Primeira tarefa: avaliar a leitura e identificar riscos ou conformidade.
    avaliar = Task(
        description=(
            "Analise a leitura abaixo. Sensor: {sensor}. Valor: {valor} {unidade}. "
            "Dispositivo: {dispositivo}. Timestamp: {timestamp}. Tópico MQTT: {topico}. "
            "A especificação válida é de {minimo} °C a {maximo} °C, inclusive. "
            "Determine se o valor está DENTRO ou FORA da especificação. "
            "Explique o impacto operacional sem inventar dados."
        ),
        expected_output=(
            "Análise estruturada contendo status (DENTRO/FORA), valor, faixa, "
            "risco ou benefício, nível de prioridade e recomendação."
        ),
        agent=analista,
    )

    # Segunda tarefa: redigir o relatório para sustentação ou direção.
    # O contexto recebe o resultado da tarefa de avaliação.
    gerar_relatorio = Task(
        description=(
            "Com base na análise anterior, escreva um relatório em Markdown. O sistema "
            "já calculou o status como {status} e o destinatário como {destinatario}; "
            "respeite esses valores. Se o status for FORA, direcione o relatório "
            "à equipe de sustentação, use o título 'Relatório de Alerta de Sensor' "
            "e inclua resumo do desvio, evidências, impacto potencial, prioridade, "
            "ações imediatas, investigação sugerida e critério de normalização. "
            "Se o status for DENTRO, direcione à direção, use o título 'Relatório "
            "de Conformidade e Impactos Positivos' e inclua resumo da conformidade, "
            "evidências, impactos positivos para a operação, recomendação de "
            "continuidade e próximos passos. Não crie números que não estejam na "
            "leitura ou especificação. Termine com uma decisão recomendada ao "
            "destinatário."
        ),
        expected_output="Relatório executivo completo em Markdown, em português.",
        agent=redator,
        context=[avaliar],
    )

    # A execução sequencial garante que o redator receba primeiro a análise.
    return Crew(
        agents=[analista, redator],
        tasks=[avaliar, gerar_relatorio],
        process=Process.sequential,
        verbose=True,
    )


def generate_report(measurement: dict) -> str:
    """Executa a equipe para uma medição normalizada."""
    # Cria uma nova execução da equipe para cada mensagem MQTT recebida.
    crew = build_crew()
    result = crew.kickoff(
        inputs={
            **measurement,
            "minimo": TEMPERATURE_MIN_C,
            "maximo": TEMPERATURE_MAX_C,
        }
    )
    return result.raw
