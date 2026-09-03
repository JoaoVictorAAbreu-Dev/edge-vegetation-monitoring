# Usa uma imagem Python enxuta e reproduzível.
FROM python:3.11-slim

# Evita arquivos .pyc e mantém os logs visíveis no terminal.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Define uma pasta padrão para a aplicação dentro do container.
WORKDIR /app

# Instala dependências primeiro para aproveitar o cache do Docker.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia somente os arquivos necessários para execução.
COPY app ./app
COPY reports ./reports

# Cria o diretório de saída dos relatórios e executa o consumidor MQTT.
CMD ["python", "-m", "app.main", "ouvir"]
