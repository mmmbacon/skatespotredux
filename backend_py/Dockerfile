FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python deps
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . ./backend_py

EXPOSE 3000
CMD ["uvicorn", "backend_py.app.main:app", "--host", "0.0.0.0", "--port", "3000"] 