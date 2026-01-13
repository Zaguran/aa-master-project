FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including poppler-utils for PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file from web/ directory
COPY web/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from web/
COPY web/ .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
