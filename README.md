# Astronomy Event Tracker with Personalized Alerts

Predicts upcoming celestial events for a specific location, works out whether each is
actually *visible* from there — accounting for the horizon, darkness, and (for the ISS)
Earth's shadow — and emails personalized alerts ahead of visible events.

The ISS-pass system is complete end to end: it pulls live orbital data, computes passes
for your coordinates, decides which are genuinely watchable, stores them, and emails you
before a visible pass — all on an automatic schedule.

## How it works

Two pipelines meet at the database. A scheduled **ingestion** pipeline fetches fresh
orbital data, computes passes, evaluates visibility, and stores the results. An **alert**
pipeline reads upcoming visible passes and emails them, never sending a duplicate.

```
CelesTrak (orbital data) ─┐
JPL ephemeris (Sun) ──────┤→ compute passes + visibility → SQLite → alert engine → email
scheduler (every 2h) ─────┘
```

## Tech stack

| Concern         | Choice                  | Notes |
|-----------------|-------------------------|-------|
| Astronomy       | Skyfield (+ DE421)      | SGP4 passes and Sun position, computed locally |
| Database        | SQLite + SQLAlchemy 2.0 | typed ORM, single-file store |
| Scheduling      | APScheduler             | runs the refresh + alert cycle |
| Data fetch      | httpx                   | orbital-data download with caching |
| Alerts          | smtplib + .env          | email via SMTP; secrets kept out of Git |
| Web API (planned) | FastAPI               | Phase 3 |

## Project structure

```
astronomy-tracker/
├── app/
│   ├── core/         # astronomy engine (passes + visibility) and database/models
│   ├── ingestion/    # TLE fetcher, pass ingestion, scheduler
│   └── alerts/       # notifiers (console, email) and the alert engine
├── data/             # cached orbital data + ephemeris (git-ignored)
├── docs/             # proposal, SRS, decision log
├── scripts/          # spike + inspection scripts
└── tests/
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

Create a `.env` in the project root for email alerts:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_gmail_app_password
ALERT_TO=you@gmail.com
```

## Usage

```bash
python init_db.py                       # create the database tables
python -m app.ingestion.iss_ingest      # fetch + compute + store passes
python -m scripts.show_passes           # list passes with visibility reasoning
python -m app.ingestion.scheduler       # run the automatic refresh + alert loop
```

## Status / roadmap

- [x] **Phase 0** — spike: compute an ISS pass for a location
- [x] **Phase 1** — database, ingestion pipeline, live data fetch, scheduler
- [x] **Phase 2** — visibility engine (Sun/darkness/shadow) + automated email alerts
- [ ] **Phase 3a** — meteor showers and eclipses
- [ ] **Phase 3b** — FastAPI web interface, multi-user locations
