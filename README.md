# backend

fastapi · pydantic · mvc.

## run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

openapi docs at http://localhost:8000/docs.

## endpoints (phase 1)

- `GET /health` → `{ "status": "ok", "env": "dev" }`
- `GET /lessons` → `{ "lessons": [...] }` (mock)

## structure

```
main.py           app factory + middleware
core/             config
routes/           http layer (thin, no logic)
controllers/      orchestrates services → views
services/         business logic
models/           pydantic schemas / domain types
views/            response shapes
```
