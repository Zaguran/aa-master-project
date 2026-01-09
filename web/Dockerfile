FROM python:3.11-slim

WORKDIR /app

# Instalace systémových věcí
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopírujeme soubor z adresáře web/ do aktuálního adresáře v kontejneru
COPY web/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Kopírujeme vše ostatní z web/
COPY web/ .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]