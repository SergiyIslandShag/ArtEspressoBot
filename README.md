# ArtEspressoBot

Telegram bot for ordering ingredients and service requests, with Postgres storage and admin tools.

## Local run (Windows)

Create venv and install dependencies:

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` (you can start from `.env.example`) and run:

```bash
python -m bot.main
```

## Database & migrations

This project uses Postgres + Alembic. Once configured, run migrations with:

```bash
alembic upgrade head
```

## VPS deploy (systemd)

See `deploy/VPS_DEPLOY.md`.