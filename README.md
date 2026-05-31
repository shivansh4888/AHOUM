# ConvEval-300

A Dockerized, GitHub-ready conversation evaluation system for scoring every conversation turn across an enriched facet registry.
Currently using groq apis but can be later switched to complete local system with a small design change.
## Quickstart

```bash
cp .env.example .env
# paste your Groq API key into .env
./start.sh
```

Frontend: http://localhost:3000 
or  Maybe at http://localhost:3001/evaluate depending on port availability 

Backend: http://localhost:8000  
OpenAPI: http://localhost:8000/docs

## Architecture

FastAPI accepts evaluations, Celery runs the pipeline, PostgreSQL stores jobs/results, Redis brokers work, Groq serves the chat-completions model through an OpenAI-compatible API, a lightweight lexical/hash router routes facets, and Next.js renders the dashboard.

Default Groq model:

```text
llama-3.1-8b-instant
```

You can change it in `.env` with `GROQ_MODEL`. The project no longer downloads local Ollama models, so startup does not consume several GB for model storage.

The default install intentionally avoids PyTorch, sentence-transformers, and FAISS so Docker does not download hundreds of megabytes of ML runtime. If you later want the optional vector router, install `backend/requirements-optional-vector.txt` and set `ROUTER_BACKEND=faiss`.

## API

`POST /api/evaluate`, `GET /api/results/{id}`, `GET /api/facets`, `GET /api/facets/{id}`, `GET /api/conversations`, `POST /api/conversations`, `DELETE /api/conversations/{id}`, `WS /ws/progress/{id}`.

## Compliance Matrix

| Constraint | Status |
|---|---|
| Evaluate every turn | Orchestrator persists each turn |
| ~300 facets | Source CSV is preserved in `data/Facets Assignment.csv`; preprocessor exports 369 enriched facets |
| Score scale | Five ordered integers, `-2..2` |
| 300 scored facets | Router scores 300 facets per turn by default via `MAX_ROUTER_FACETS=300` |
| 5000+ facets | Lightweight router bounds scoring without architectural changes |
| Hosted Groq model | `GROQ_MODEL=llama-3.1-8b-instant` by default |
| No one-shot prompting | Separate context, scoring, critique/ensemble passes |
| Confidence | Enabled by default with ensemble confidence intervals and agreement |
| Rate-limit handling | Large 300-facet runs use local deterministic scoring with confidence to avoid hosted API stalls |
| Docker | frontend/backend/worker/redis/postgres/nginx |
| Sample UI | Next.js analytical dashboard |
| 50 conversations | `conversations/` plus `conversations.zip` |

## Development

```bash
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

Required environment:

```bash
export GROQ_API_KEY=gsk_...
export GROQ_MODEL=llama-3.1-8b-instant
export ROUTER_BACKEND=lexical
```

## Benchmarks

```bash
python3 benchmarks/run_all.py
```
