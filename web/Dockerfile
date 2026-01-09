FROM python:3.11-slim

WORKDIR /app

# 1. Instalace systémových nástrojů
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Kopírování requirements
# V kontextu ./web je requirements.txt přímo "po ruce"
COPY requirements.txt .

# 3. Instalace python balíčků
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kopírování všeho ostatního ze složky web/ (app.py atd.)
COPY . .

# 5. Spuštění
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]