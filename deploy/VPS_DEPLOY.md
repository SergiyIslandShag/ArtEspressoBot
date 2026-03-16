## VPS deploy (Ubuntu + systemd)

Below is a straightforward deploy recipe for a typical Ubuntu VPS.

### 1) System packages

Install Python and Postgres client tools:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip postgresql-client
```

### 2) Project directory

Choose a directory (example: `/opt/artespresso-bot`) and copy the repo there.

```bash
sudo mkdir -p /opt/artespresso-bot
sudo chown -R "$USER":"$USER" /opt/artespresso-bot
cd /opt/artespresso-bot
```

### 3) Virtualenv + deps

```bash
cd /opt/artespresso-bot/ArtEspressoBot
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### 4) Configure `.env`

Create `/opt/artespresso-bot/ArtEspressoBot/.env` based on `.env.example` and fill:

- `BOT_TOKEN`
- `DATABASE_URL` (example: `postgresql+asyncpg://user:pass@127.0.0.1:5432/artespresso`)
- `GROUP_CHAT_ID`
- `ADMIN_TELEGRAM_IDS`

### 5) Run migrations

```bash
cd /opt/artespresso-bot/ArtEspressoBot
. .venv/bin/activate
alembic upgrade head
```

### 6) systemd service

Copy the unit file and enable it:

```bash
sudo cp /opt/artespresso-bot/ArtEspressoBot/deploy/systemd/artespresso-bot.service /etc/systemd/system/artespresso-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now artespresso-bot.service
```

Check logs:

```bash
sudo journalctl -u artespresso-bot -f
```

### 7) Telegram group setup

- Add the bot to your group.
- Ensure it can send messages (member is usually enough; admin may be needed in some group configs).
- Set `GROUP_CHAT_ID` in `.env`.

