# backend

fastapi with pydantic v2, strict mvc. state is in-memory for now, so a
restart clears it; postgres is the planned next step.

## run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

openapi docs at http://localhost:8000/docs.

`/cv/*` imports the shared vision package from the sibling folder. the
comparator itself only needs numpy; install the vision requirements only if
you plan to run server-side tracking.

## tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

covers routes, controllers, services, and core, with integration tests
running against the real app through a test client.

## endpoints

- `GET /health`
- `GET /lessons`
- `POST /cv/evaluate` scores 21 landmarks against a reference gesture
- `GET /cv/results?limit=N&user_id=X` recent evaluations, optionally
  filtered to one user
- `GET /routines`, `GET /routines/{id}`
- `POST /routines` create a custom routine (owner in `created_by`)
- `PUT /routines/{id}` update; the body must carry the owner's
  `created_by`, anything else gets a 403
- `DELETE /routines/{id}?created_by=X` same ownership rule, via query
  param since delete has no body
- `POST /progress` log an attempt; accepts an idempotency key (replays
  return the original response) and the client's `tz_offset_minutes` so
  streak days follow the learner's clock
- `GET /progress/{profile_id}?limit=N` summary plus recent records
- `PUT /progress/{profile_id}/goal` set the daily goal target (1 to 50)
- `GET /profiles`, `POST /profiles`, `GET /profiles/{id}`
- `GET /analytics/{profile_id}` accuracy trend, weak gestures, finger heat
- `POST /study/sessions` tally a camera-free study session (browse or quiz)
- `GET /study/{profile_id}` study totals per deck plus quiz accuracy

## configuration

all optional in dev. see `.env.example` for the full list.

- `HIGHFIVE_ENV` environment label (dev, staging, prod)
- `HIGHFIVE_CORS_ORIGINS` comma-separated allowed origins
- `HIGHFIVE_RATE_LIMIT` token bucket for the open POST endpoints, format
  `<requests>/<window-seconds>` per client ip; unset means disabled

## structure

```
main.py           app factory plus middleware composition
core/             config, request ids, rate limit, server timing,
                  idempotency cache
routes/           http layer, thin, no logic
controllers/      orchestrate services into responses
services/         business logic (progress, analytics, profiles,
                  routines, cv)
models/           domain types
views/            request/response schemas
tests/            pytest suite
```

every response carries an `x-request-id` for log correlation and a
`server-timing` header with the in-app duration.
