#!/usr/bin/env bash
# Construye y corre los tests del sistema de actualizaciones en Docker.
# Uso: ./docker/run_tests.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "=== Construyendo imagen Docker ==="
docker build -t lubricentro-test -f "$REPO_ROOT/docker/Dockerfile" "$REPO_ROOT"

echo "=== Corriendo tests del updater + DB ==="
docker run --rm \
  -v "$REPO_ROOT/docker/test_updater.py:/app/docker/test_updater.py:ro" \
  -v "$REPO_ROOT/docker:/app/docker:ro" \
  lubricentro-test \
  python -m pytest /app/tests/ /app/docker/test_updater.py -v

echo "=== Todos los tests pasaron ==="
