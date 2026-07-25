FROM python:3.12-slim

# Dependencias del sistema: tar nativo (bsdtar) y sqlite para inspeccionar DBs
RUN apt-get update && apt-get install -y --no-install-recommends \
    tar \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar solo requirements primero para cache de Docker
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo del proyecto
COPY database.py /app/
COPY updater.py /app/
COPY app.py /app/
COPY pages/ /app/pages/
COPY style.py /app/
COPY tickets.py /app/
COPY tests/ /app/tests/

# Asegurar que los tests del updater corren con paths en /app
ENV PYTHONPATH=/app

# Default: correr pytest + tests del updater
CMD ["python", "-m", "pytest", "/app/tests/", "/app/docker/test_updater.py", "-v"]
