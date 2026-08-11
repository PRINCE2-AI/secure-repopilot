# Deployment Guide

Secure RepoPilot can run locally through Python or through Docker.

## Local API

```bash
uvicorn app.api:api --host 0.0.0.0 --port 8000
```

## Local Dashboard

```bash
streamlit run app/ui.py
```

## Docker API

```bash
docker build -t secure-repopilot .
docker run --env-file .env -p 8000:8000 secure-repopilot
```

## Docker Compose

```bash
docker compose up --build
```

Services:

| Service | URL |
| --- | --- |
| API | http://localhost:8000 |
| Dashboard | http://localhost:8501 |

## Notes

- Start from `.env.example` and create `.env` before running Docker Compose.
- The project keeps OpenAI use optional for local portfolio demos and tests.
- The `data/` and `outputs/` directories are mounted as local volumes.
- Production use should run repository mutation inside a stronger sandbox.
