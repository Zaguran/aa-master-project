FROM python:3.11-slim

WORKDIR /app

# Instalace systémových závislostí
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopírujeme soubor z lokálního adresáře do kontejneru
# Tečka na konci je důležitá - znamená "tento adresář v kontejneru"
COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

# Kopírujeme zbytek souborů (app.py atd.)
COPY . .

EXPOSE 8501

# Tady pozor: tvůj soubor se jmenuje app.py, nikoliv main.py
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]