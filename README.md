# Astronomy Event Tracker with Personalized Alerts

Predicts upcoming celestial events — ISS passes, meteor showers, eclipses — for a
user's exact location, works out whether each event is actually *visible* from
there (accounting for the horizon, darkness/twilight, and the Moon), and sends
personalized alerts.

## Why this project is interesting

Most of the value lives in the backend: it turns raw orbital data into
location-specific predictions using real coordinate mathematics, aggregates data
from several sources on a schedule, and computes visibility rather than just
listing events that happen "somewhere on Earth."

## Tech stack

| Concern            | Choice        | Why |
|--------------------|---------------|-----|
| Astronomy math     | Skyfield      | Satellite passes *and* sun/moon/twilight in one library, computed locally |
| Web API            | FastAPI       | Async, typed, auto-generates interactive API docs |
| Scheduled jobs     | APScheduler   | Runs the periodic data-ingestion jobs |
| Database           | *to be decided in Phase 1* | |

## Project structure

```
astronomy-tracker/
├── app/
│   ├── core/         # astronomy engine: coordinate math + visibility logic
│   ├── ingestion/    # scheduled jobs that pull/compute event data
│   └── api/          # FastAPI web layer
├── data/             # cached orbital data + curated meteor/eclipse datasets
├── docs/             # all project documents (proposal, SRS, decisions, ...)
├── scripts/          # one-off scripts (e.g. the Phase 0 spike)
└── tests/            # test cases
```

## Current status

**Phase 0 (spike) — done.** `scripts/spike_iss_pass.py` computes ISS passes over a
location from a real orbital element set, proving the hardest part works end to end.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/spike_iss_pass.py
```

## Roadmap

- [x] **Phase 0** — spike: compute one satellite pass for a location
- [ ] **Phase 1** — MVP: scheduled ISS ingestion + single-event alert, end to end
- [ ] **Phase 2** — full visibility engine (twilight + moon), meteor showers, eclipses
- [ ] **Phase 3** — FastAPI + frontend, deployment, final documentation
