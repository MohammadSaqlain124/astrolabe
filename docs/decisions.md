# Decision Log

A running record of *why* we made each significant choice. When someone (a
reviewer, a future you) asks "why is it built this way," the answer is here.
Newest entries at the bottom.

---

### D-001 — Language: Python
**Date:** 2026-07-12
**Decision:** Build the project in Python.
**Why:** Central to the author's career direction; strongest astronomy library
ecosystem; the author is already comfortable in it, so learning effort goes into
the domain (astronomy) rather than the language.
**Alternative considered:** Node.js/MERN — rejected for this project because it
would have required two separate libraries for the astronomy and offered no
career advantage over Python here.

---

### D-002 — Astronomy library: Skyfield
**Date:** 2026-07-12
**Decision:** Use Skyfield for all astronomy computation.
**Why:** Single library covers *both* satellite propagation (ISS passes via SGP4)
and sun/moon/twilight/rise-set. Computes locally — no API key, no rate limits.
Built on the same professional-grade SGP4 + JPL ephemeris machinery used in real
astrodynamics work.

---

### D-003 — Web framework: FastAPI (over Flask)
**Date:** 2026-07-12
**Decision:** Use FastAPI for the web/API layer (Phase 3).
**Why:** Async by design; uses Python type hints (teaches typed Python);
auto-generates interactive API documentation from the code, which directly
supports the "documents alongside" goal.

---

### D-004 — Compute ISS passes ourselves (don't depend on a pass-prediction API)
**Date:** 2026-07-12
**Decision:** Fetch raw orbital elements (TLE) and compute passes with SGP4
locally, rather than calling a third-party "next pass" API.
**Why:** The long-standing free pass-prediction API (open-notify) was retired.
Computing passes ourselves is more robust, removes an external dependency, and is
the exact coordinate-math depth this project is meant to showcase.

---

### D-005 — Finding: TLE staleness is a first-class requirement
**Date:** 2026-07-12
**Decision:** Ingestion must refresh orbital data on a schedule and reject data
older than a set threshold.
**Why:** The Phase 0 spike propagated a ~100-day-old orbital snapshot and produced
mechanically valid but physically unreliable predictions. This confirmed, by
experiment, that data freshness is not optional. Recorded as a risk in the
proposal and as a hard requirement for the ingestion module.

---

---

### D-006 — Database: SQLite + SQLAlchemy 2.0
**Date:** 2026-07-13
**Decision:** Use SQLite as the database, accessed through the SQLAlchemy 2.0 ORM.
**Why:** Zero setup (SQLite is a single file), while SQLAlchemy is a career-valuable
ORM skill that ports directly to PostgreSQL later. The modern typed `Mapped[...]`
style also reinforces typed Python.
**Alternatives considered:** MongoDB (already known, but less growth) and PostgreSQL
(production-grade, but adds setup overhead now). SQLite migrates to Postgres later
with minimal change.

---

### D-007 — Ingestion strategy: delete-and-replace for recomputable data
**Date:** 2026-07-13
**Decision:** On each ISS ingestion run, delete existing `iss_pass` rows for the
location and insert freshly computed ones.
**Why:** ISS passes are predictions, recomputed from the current orbit every run, so
there is no history to preserve. Delete-and-replace makes ingestion idempotent (safe
to run repeatedly) without duplicate-detection logic.
**Consequence:** Alert-tracking cannot live on the event rows (they are wiped each
run) — see D-009.

---

### D-008 — Visibility model: dark sky AND sunlit station, judged at peak
**Date:** 2026-07-13
**Decision:** A pass is "visible" when, at its peak moment, (a) the observer's Sun is
below -6 degrees (past civil twilight) AND (b) the ISS is sunlit (not in Earth's
shadow). Sun position comes from the JPL DE421 ephemeris via Skyfield.
**Why:** These two conditions together are what make the ISS actually observable, and
they correctly explain why visible passes cluster in the ~1-2 hours after dusk or
before dawn.
**Known simplification:** visibility is evaluated only at the peak instant, not across
the whole pass. A pass could enter shadow partway through. Acceptable for the MVP;
listed under future work.

---

### D-009 — Alert de-duplication: a separate SentAlert table
**Date:** 2026-07-13
**Decision:** Record sent alerts in a dedicated `sent_alerts` table, keyed by a pass
identity string (`iss_pass@<peak-time-to-the-minute>`), rather than a flag on the
event row.
**Why:** The events table is wiped and rebuilt on every ingestion (D-007), so a flag
there would be lost and passes would be re-alerted. A separate table survives rebuilds.
The minute-level key stays stable even when a fresh orbit shifts the peak by seconds.

---

### D-010 — Notification: pluggable notifier, email via SMTP with secrets in .env
**Date:** 2026-07-13
**Decision:** The alert engine depends on a notifier object exposing `send(subject,
body)`. Two implementations exist: `ConsoleNotifier` (development) and `EmailNotifier`
(SMTP/Gmail). Credentials are read from environment variables loaded from a
git-ignored `.env` file.
**Why:** The engine is decoupled from the delivery channel, so swapping console for
email required no engine changes. Keeping secrets in `.env` (never committed) is the
standard, safe way to handle credentials.

---

### D-011 — Multi-type event model: nullable columns + JSON details
**Date:** 2026-07-13
**Decision:** Hold ISS passes, meteor showers, and lunar eclipses in one `events`
table. Make the ISS-only columns (`peak_altitude_deg`, `sun_altitude_deg`,
`iss_sunlit`) nullable and add a `details` JSON column for each type's own data.
**Why:** A single `event_type`-tagged table keeps queries and the alert engine
uniform across event kinds, while `details` avoids a sprawl of type-specific columns.

---

### D-012 — Meteor showers from a curated dataset; eclipses computed natively
**Date:** 2026-07-13
**Decision:** Seed meteor showers from a curated JSON file (radiant, ZHR, peak date)
and compute per-location visibility by sampling the peak night. Compute lunar eclipses
directly with Skyfield's `eclipselib`.
**Why:** No reliable free API exists for meteor showers, so known annual data is
carried as a dataset; eclipses, by contrast, fall straight out of ephemeris geometry.

---

### D-013 — Web API: compute-on-demand, thin layer over a service function
**Date:** 2026-07-14
**Decision:** Expose a FastAPI app. `GET /events` computes events live for any
lat/lon via `events_service.upcoming_events` without touching the database;
`POST /subscribe` upserts a user. Request validation uses FastAPI/Pydantic.
**Why:** Computing on demand makes the read API work for any location instantly.
Keeping the logic in a service function (not the route) keeps the web layer thin and
testable.

---

### D-014 — Multi-user alerting: per-subscriber ingestion and per-user dedup
**Date:** 2026-07-14
**Decision:** The scheduler ingests events for each unique subscriber location; the
alert engine loops over active users, matches events at their coordinates, sends to
their email, and keys de-duplication by `user{id}:...` so users are independent.
Lead time varies by event type (1 day for ISS, 3 for showers/eclipses).
**Why:** Turns the tool into a real multi-user service where each person gets alerts
for their own location without one user's alert suppressing another's.

---

### D-015 — Configurable database URL for testability
**Date:** 2026-07-14
**Decision:** `database.py` reads `DATABASE_URL` from the environment (defaulting to
the real SQLite file). Tests point it at a throwaway database via `conftest.py`.
**Why:** Lets the automated test suite run against an isolated database without
touching real data — configuration via environment is also the standard deployment
pattern.
