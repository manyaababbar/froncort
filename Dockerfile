FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --force-reinstall uvicorn[standard]==0.24.0

COPY main.py .
COPY sql_agent/ ./sql_agent/
COPY data/ ./data/
COPY subagents/ ./subagents/
COPY functions/ ./functions/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]