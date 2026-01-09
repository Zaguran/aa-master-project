# Použijeme stabilní verzi Pythonu
FROM python:3.11-slim

WORKDIR /app

# Instalujeme jen to, co je nezbytně nutné
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopírování requirements a instalace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování zbytku aplikace
COPY . .

# Port pro Streamlit
EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]