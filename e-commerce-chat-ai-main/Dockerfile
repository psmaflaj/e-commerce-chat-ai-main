FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Código
COPY . .

EXPOSE 8000

# Arranque del servidor
CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
