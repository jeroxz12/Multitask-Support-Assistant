# Support Agent Assistant

CLI assistant for customer support agents. It takes a customer question, calls the OpenAI API, and prints a structured JSON response.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`. Optionally set `OPENAI_MODEL` (default: `gpt-4o-mini`).

## Run

```bash
python3 -m src.support_assistant "My payment was rejected. Why?"
```

Each run appends one row to `metrics/metrics.csv` (tokens, latency, estimated cost, model, timestamp, and status). The console still prints only the SupportResponse JSON.

Injection attempts are blocked locally and logged in `metrics/safety.csv`. See `docs/safety.md`.

## Tests

```bash
python3 -m pytest
```

The tests cover:
- the happy path (valid `SupportResponse`, normal question allowed, prompt loaded)
- invalid schema payloads
- cost estimation
- prompt injection / safety fallbacks

They do not call the OpenAI API.
