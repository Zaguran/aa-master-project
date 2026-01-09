FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/list/apt/lists/*

COPY web/requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "web/app.py", "--server.port=8501", "--server.address=0.0.0.0"]