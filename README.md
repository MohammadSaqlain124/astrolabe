# Astronomy Event Tracker with Personalized Alerts

A location-aware service that predicts upcoming celestial events — ISS passes, meteor
showers, and lunar eclipses — works out whether each is genuinely *visible* from a
given place, and emails subscribers before events they can actually see.

## What it does

- **Computes events for any location:** ISS passes (from live orbital data), meteor
  showers (radiant + Moon phase), and lunar eclipses (Moon above the horizon).
- **Judges real visibility:** darkness, Earth's shadow, radiant altitude, Moon
  interference — not just "an event happened somewhere."
- **Serves a web API:** `GET /events` for any lat/lon, `POST /subscribe` to register.
- **Emails subscribers automatically:** a scheduler refreshes data and sends
  per-user, per-location alerts, de-duplicated, with a lead time suited to each event.

## Architecture

```
CelesTrak (orbital data) ─┐
JPL ephemeris (Sun/Moon) ─┤→ compute + visibility → SQLite → alert engine → email
curated meteor dataset ───┘        ▲
                                   │
        FastAPI  ── GET /events (compute on demand) / POST /subscribe (users)
        scheduler ── refresh every 2h, then alert every active subscriber
```

## Tech stack

| Concern         | Choice                  |
|-----------------|-------------------------|
| Astronomy       | Skyfield (+ DE421 ephemeris) |
| Web API         | FastAPI + Uvicorn       |
| Database        | SQLite + SQLAlchemy 2.0 |
| Scheduling      | APScheduler             |
| Data fetch      | httpx                   |
| Email           | smtplib + .env secrets  |
| Tests           | pytest                  |

## Project structure

```
astronomy-tracker/
├── app/
│   ├── core/         # astronomy (iss, meteors, eclipses, sky), models, db, events_service
│   ├── ingestion/    # TLE fetcher, per-type ingestion, scheduler
│   ├── alerts/       # notifiers (console/email) + alert engine
│   └── api/          # FastAPI app
├── data/             # cached orbital data, ephemeris, meteor dataset (git-ignored where large)
├── docs/             # proposal, SRS, decision log
├── scripts/          # spike + inspection scripts
├── tests/            # pytest suite
└── conftest.py       # test configuration (isolated DB)
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate                 # Windows (source venv/bin/activate elsewhere)
pip install -r requirements.txt
```

Create a `.env` for email alerts:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

## Usage

```bash
python init_db.py                       # create database tables

# Web API (interactive docs at http://127.0.0.1:8000/docs)
uvicorn app.api.main:app --reload

# Command-line inspection
python -m scripts.show_events

# Automatic refresh + per-subscriber alerts
python -m app.ingestion.scheduler
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Status / roadmap

- [x] ISS passes, meteor showers, lunar eclipses — with per-location visibility
- [x] Email alerts for all event types (per-user, de-duplicated)
- [x] FastAPI web API with subscriptions
- [x] Automated test suite
- [ ] Web frontend (location form + event list)
- [ ] Deployment (hosted API + always-on scheduler)
- [ ] Solar eclipses; PostgreSQL migration
