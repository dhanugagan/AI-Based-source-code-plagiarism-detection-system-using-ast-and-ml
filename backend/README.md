# Backend — CodeGuard API

FastAPI service implementing the AST + ML plagiarism detection pipeline.
See the [project root README](../README.md) for full setup instructions,
architecture, and the detection pipeline explanation.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Test

```bash
pip install pytest
pytest tests/ -v
```

## Retrain the ML model

```bash
python -m app.ml.train
```

Writes `../models/plagiarism_model.joblib` and a metrics report next to it.
