# Pluto

Local-first AI receipt scanner and expense tracker. Scan a receipt image,
let a local vision model extract the data, and store expenses in SQLite
— no cloud, no account.

## Layout

```
apps/
  api/   FastAPI backend (Python)
  cli/   Cobra CLI (Go)
  web/   Web app (vinxi)
packages/
  pluto-core/   Shared models
```

## Backend (apps/api)

Python 3.11+.

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The server listens on `http://localhost:8000`. Interactive docs at
`/docs`.

### Endpoints

| Method | Path                 | Description                              |
|--------|----------------------|------------------------------------------|
| GET    | `/health`            | Liveness probe                           |
| POST   | `/scan`              | Upload image, return AI extraction       |
| GET    | `/expenses`          | List expenses (filter by month/year/cat) |
| POST   | `/expenses`          | Create an expense                        |
| PUT    | `/expenses/{id}`     | Update an expense                        |
| DELETE | `/expenses/{id}`     | Delete an expense (and its image)        |
| GET    | `/categories`        | List pre-seeded categories               |
| GET    | `/stats`             | Totals + per-category breakdown          |
| POST   | `/sync`              | Push/pull the SQLite file to a folder    |

### Configuration

The AI service talks to a local Ollama instance. Override with env vars:

- `PLUTO_OLLAMA_URL` (default `http://localhost:11434`)
- `PLUTO_OLLAMA_MODEL` (default `llama3.2-vision`)
- `PLUTO_OLLAMA_TIMEOUT` (seconds, default `30`)

### Data flow

1. Client uploads a receipt to `POST /scan`.
2. Server saves the image, calls Ollama, returns extracted fields.
3. Client confirms/edits and posts to `POST /expenses`.

If Ollama is unreachable or returns bad data, `/scan` still responds
with a 200 — `extracted` carries what was found, `errors` lists what
failed, and `needs_review` tells the UI which fields to prompt for.
