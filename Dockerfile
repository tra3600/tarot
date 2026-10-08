FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TAROT_DB=/data/tarot.db

RUN useradd --create-home --uid 1000 tarot && mkdir /data && chown tarot /data
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY tarot_bot ./tarot_bot
USER tarot

# La base SQLite (commandes, preuves de consentement aux CGV) vit dans le volume /data.
VOLUME /data
CMD ["python", "-m", "tarot_bot.telegram_bot"]
