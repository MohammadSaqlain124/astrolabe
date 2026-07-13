# Software Requirements Specification

**Project:** Astronomy Event Tracker with Personalized Alerts
**Author:** Mohd. Saqlain Hussain
**Version:** 1.0 (covers the ISS-pass MVP: Phases 0–2)
**Date:** 2026-07-13

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the Astronomy Event Tracker, a backend
service that predicts upcoming celestial events for a specific geographic location,
determines whether each event is genuinely observable from there, and sends
personalized alerts ahead of visible events. This version documents the implemented
ISS-pass system and defines the requirements that later event types and the web
interface will extend.

### 1.2 Scope
The system aggregates or computes celestial-event data, evaluates per-location
visibility using real astronomical geometry, stores results, and delivers alerts.
The current release covers International Space Station (ISS) passes end to end.
Meteor showers, eclipses, and a multi-user web interface are planned extensions and
are described here only as future scope.

### 1.3 Definitions
- **TLE (Two-Line Element set):** a compact snapshot of a satellite's orbit at a
  specific epoch, propagated forward in time by the SGP4 model.
- **Pass:** an interval during which a satellite is above a defined elevation at the
  observer's location, described by rise, peak, and set events.
- **Altitude / Azimuth:** an object's height above the horizon and its compass
  direction, from the observer's viewpoint.
- **Ephemeris:** a precomputed table of Solar-System body positions over time (here,
  JPL DE421) used to locate the Sun.
- **Visible pass:** a pass occurring while the observer's sky is dark and the ISS is
  lit by the Sun.

### 1.4 References
CelesTrak orbital-element service; NASA/JPL DE421 ephemeris; Skyfield astronomy
library documentation; the project Decision Log (`docs/decisions.md`).

---

## 2. Overall Description

### 2.1 Product perspective
The system is a self-contained Python backend composed of four cooperating parts: a
scheduled ingestion pipeline, an astronomy computation core, a relational data store,
and an alert engine. Two pipelines meet at the database — one that pulls and computes
event data on a schedule, and one that reads it to serve results and fire alerts.

### 2.2 Product functions (summary)
Fetch fresh orbital data; compute ISS passes for a location; evaluate each pass's
visibility; store events; detect upcoming visible passes and send de-duplicated
alerts; run the whole cycle automatically on a schedule.

### 2.3 User classes
- **Sky-watcher (end user):** receives alerts for visible events at their location.
- **Operator/developer:** configures location and credentials, runs and maintains the
  service.

### 2.4 Constraints
Python 3.13; SQLite via SQLAlchemy 2.0; Skyfield for astronomy; free external data
sources subject to their rate limits and terms; credentials held only in a local,
git-ignored `.env` file.

### 2.5 Assumptions and dependencies
Network access is available for orbital-data refresh and email delivery; the JPL
ephemeris file is downloaded once and cached locally; all datetimes are stored as
UTC and converted to the user's timezone only for display.

---

## 3. Functional Requirements

**FR-1 — Orbital data acquisition.** The system shall fetch the ISS Two-Line Element
set from CelesTrak, identifying itself with a descriptive User-Agent and not
re-downloading data less than two hours old.

**FR-2 — Data validation.** The system shall validate fetched data as a well-formed
TLE before overwriting the stored copy, and shall preserve the existing copy if
validation fails.

**FR-3 — Pass computation.** For a given latitude and longitude, the system shall
compute the ISS's rise, peak, and set events over a configurable time window, using
SGP4 propagation, keeping only passes whose peak elevation exceeds a configurable
minimum.

**FR-4 — Visibility evaluation.** For each pass, the system shall determine visibility
at the peak moment as the conjunction of (a) the observer's Sun altitude below the
darkness threshold and (b) the ISS being sunlit.

**FR-5 — Persistence.** The system shall store each pass with its location, timing,
peak elevation, Sun altitude, sunlit state, and visibility verdict.

**FR-6 — Idempotent ingestion.** Re-running ingestion for a location shall not create
duplicate pass records.

**FR-7 — Alert detection.** The system shall identify visible passes whose peak falls
within a configurable lead window and which have not already been alerted.

**FR-8 — Alert delivery.** The system shall deliver each due alert through a
configurable notifier (console or email), with human-readable local-time details.

**FR-9 — Alert de-duplication.** The system shall never send more than one alert for
the same pass, tracked independently of the (rebuilt) event records.

**FR-10 — Scheduling.** The system shall run the fetch, compute, and alert cycle
automatically at a fixed interval.

---

## 4. Non-Functional Requirements

**NFR-1 — Accuracy.** Pass predictions shall be based on orbital data no older than
the refresh interval; the system shall not present predictions from data beyond its
validity window without refresh.

**NFR-2 — Reliability.** A failure in an external dependency (data source or mail
server) shall not corrupt stored data; validation and transactional writes protect
integrity.

**NFR-3 — Security.** No credential shall appear in source code or version control;
all secrets are read from the environment via a git-ignored `.env` file.

**NFR-4 — Maintainability.** The astronomy core shall be independent of the database
and delivery layers, so each can be tested or replaced in isolation.

**NFR-5 — Portability.** The data store (SQLite) and secrets handling shall allow
migration to a server database and hosted environment without changes to the
computation logic.

**NFR-6 — Good external-citizenship.** The system shall respect published rate limits
and caching guidance of the data providers it consumes.

---

## 5. External Interface Requirements

- **CelesTrak (HTTPS):** source of ISS orbital elements; consumed read-only with a
  descriptive User-Agent and ≥2-hour cache.
- **JPL DE421 ephemeris (file):** Sun position for visibility; downloaded once, cached.
- **SMTP server (Gmail):** outbound alert email over STARTTLS, authenticated with an
  app password from the environment.
- **Future — HTTP/REST API:** a web interface for per-user location and preferences.

---

## 6. Data Model (current)

- **events:** id, event_type, name, latitude, longitude, start_utc, peak_utc, end_utc,
  peak_altitude_deg, sun_altitude_deg, iss_sunlit, visible, created_at.
- **sent_alerts:** id, alert_key (unique), sent_at.

All datetimes are UTC. `event_type` allows one table to hold multiple event kinds as
the system grows.

---

## 7. Known Limitations
Visibility is judged at the peak instant only (not across the whole pass); the pass
identity used for de-duplication is stable to the minute; the scheduler runs as a
single foreground process. Each is acceptable for the MVP and tracked for future work.

---

## 8. Future Scope
Meteor-shower and eclipse ingestion with per-location visibility; Moon-phase
interference in the visibility score; a FastAPI web interface with multi-user
locations and preferences; migration to PostgreSQL and a hosted, always-on scheduler;
push notifications in addition to email.
