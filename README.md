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

## endpoints

- `GET /health` → `{ "status": "ok", "env": "dev" }`
- `GET /lessons` → `{ "lessons": [...] }` (mock)
- `POST /cv/evaluate` → `{ accuracy, band, incorrect_points, suggestion }`
  · body: `{ gesture_id, landmarks: [{x,y,z}]*21, user_id? }`
- `GET /cv/results?limit=N` → recent evaluations (in-memory ring buffer)
- `GET /routines` → list scenarios
- `GET /routines/{id}` → routine + ordered steps
- `POST /progress` → log an attempt against a `profile_id`; returns fresh `summary`
- `GET /progress/{profile_id}?limit=N` → summary + recent records
- `GET /profiles` · `POST /profiles` · `GET /profiles/{id}` — multi-profile management (phase 5)

`/cv/*` imports the shared `/vision` module. install its deps
(`pip install -r ../vision/requirements.txt`) if you plan to run server-side
tracking — the comparator itself only needs numpy.

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
