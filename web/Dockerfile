FROM python:3.11-slim

WORKDIR /app

# Instalace systémových věcí
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
	poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 1. Kopírujeme požadavky (předpokládám, že jsou ve web/requirements.txt)
COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Kopírujeme obsah složky web přímo do /app
COPY web/ .

# 3. KOPÍRUJEME SLOŽKU AGENTS (To je ta chybějící část)
# Tato řádka vezme složku agents z kořene projektu a dá ji do /app/agents v kontejneru
COPY agents/ ./agents/

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]