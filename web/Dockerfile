FROM python:3.11-slim

WORKDIR /app

# Set Python path for proper imports
ENV PYTHONPATH="/app"

# Install system dependencies including poppler-utils for PDF processing and libpq-dev for PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    poppler-utils \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file from web/ directory
COPY web/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy agents directory for imports
COPY agents/ /app/agents/

# Copy application code from web/
COPY web/ .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
