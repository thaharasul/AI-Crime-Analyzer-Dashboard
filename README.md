# AI Crime Analyzer Dashboard

A Flask-based crime analytics platform: dashboard + charts + map, an ML
crime-category predictor, a RAG-grounded AI assistant (Gemini), and a
minimal multi-agent layer (Analyst / Prediction / Recommendation /
Coordinator) that powers the executive PDF briefing.

## What's included vs. trimmed

This is a **scoped-down** build for a tight deadline. Included:
dashboard analytics + map, ML prediction with evaluation metrics, RAG
assistant, CSV/PDF report export, login, and a lightweight 4-agent
system. Trimmed to save time: Docker, PostgreSQL config, a Settings
page, Excel export, and LangGraph (the coordinator is plain Python -
swapping in LangGraph later only touches `agents/coordinator.py`).

## Project structure

```
app.py                 Flask entry point / blueprint registration
config.py               Paths, env vars, constants

database/
  db.py                 SQLite connection + schema
  seed_data.py           Synthetic dataset generator (1,800 records)

ml/
  train_model.py         Trains + evaluates RandomForest, saves pickle
  predictor.py            Loads model, serves predictions

rag/
  knowledge_base/         IPC sections + sample analyst reports (.txt)
  ingest.py                Chunk -> embed -> store in ChromaDB
  retriever.py             Query-time retrieval

agents/
  analyst_agent.py         Pattern/anomaly detection (pandas)
  prediction_agent.py      Wraps ml/predictor.py
  recommendation_agent.py  Gemini-backed recommendations (+ fallback)
  coordinator.py           Routes requests to the right agent(s)

services/
  gemini_service.py        Gemini API wrapper (single call site)
  assistant_service.py     RAG: retriever + Gemini, grounded answers

api/
  routes_auth.py, routes_dashboard.py, routes_prediction.py,
  routes_assistant.py, routes_reports.py   Flask blueprints

utils/
  report_generator.py      CSV export + PDF executive briefing

templates/                 Jinja2 HTML (Bootstrap 5)
static/css, static/js       Styling + Chart.js/Leaflet frontend logic
data/                       Generated CSV + SQLite DB (gitignore in prod)
models_store/                Trained model pickle + metrics.json
```

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste your Gemini key into GEMINI_API_KEY=

python -m database.seed_data       # generates + loads sample crime data
python -m ml.train_model           # trains the RandomForest predictor
python -m rag.ingest                # builds the ChromaDB knowledge index

python app.py                       # runs on http://127.0.0.1:5000
```

Login with `admin` / `admin123` (change in `.env`).

**Note on this delivered copy:** `data/` and `models_store/` already
contain a seeded dataset and a trained model (verified working - ~61%
accuracy across 5 crime categories, well above the 20% random
baseline). The RAG index (`rag/chroma_store/`) is **not** pre-built,
because building it requires downloading the `all-MiniLM-L6-v2`
embedding model from Hugging Face, which wasn't reachable from the
sandbox this was built in. Run `python -m rag.ingest` once on your
machine (needs internet) before using the AI Assistant page - it only
needs to be run once, or again whenever you edit the `.txt` files in
`rag/knowledge_base/`.

## Production notes

- Swap `SECRET_KEY`, `ADMIN_PASSWORD` for real values before any real
  deployment; the current auth is intentionally simple (single admin
  session, no password hashing/user table).
- Run behind `gunicorn app:app` in production instead of `python app.py`.
- To move off SQLite, only `database/db.py`'s connection string needs
  to change - no other file touches the DB path directly.
