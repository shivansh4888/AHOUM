#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$ROOT"
CSV_SOURCE="${FACETS_CSV:-/home/shivansh/Downloads/Facets Assignment.csv}"
[ -f "$CSV_SOURCE" ] || { echo "Facet CSV not found: $CSV_SOURCE"; exit 1; }
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi
[ -n "${GROQ_API_KEY:-}" ] || { echo "GROQ_API_KEY is missing. Copy .env.example to .env and paste your Groq key."; exit 1; }
python3 scripts/preprocess_facets.py --input "$CSV_SOURCE" --out data
python3 scripts/generate_conversations.py
if docker compose version >/dev/null 2>&1; then COMPOSE="docker compose"; else COMPOSE="docker-compose"; fi
$COMPOSE up -d postgres redis
$COMPOSE up -d --build backend worker frontend nginx
for i in {1..40}; do curl -fsS http://localhost:8000/health >/dev/null && { echo "ConvEval-300 is running: http://localhost:3000"; exit 0; }; sleep 2; done
echo "Services started, but backend health did not respond yet."; exit 1
