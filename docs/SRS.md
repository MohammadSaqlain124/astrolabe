# Software Requirements Specification

**Project:** Astronomy Event Tracker with Personalized Alerts
**Author:** Mohd. Saqlain Hussain
**Version:** 2.0 (multi-type events, web API, multi-user alerts)
**Date:** 2026-07-14

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the Astronomy Event Tracker, a
location-aware service that predicts upcoming celestial events, determines whether
each is observable from a given location, exposes the results through a web API, and
emails registered subscribers ahead of visible events. This version supersedes v1.0
(ISS-only) and documents the implemented multi-type, multi-user system.

### 1.2 Scope
The system computes and serves three event types — ISS passes, meteor showers, and
lunar eclipses — evaluating per-location visibility for each. Users register a
location through the API and receive personalized email alerts. Solar eclipses, a web
frontend, and hosted deployment are planned extensions described under future scope.

### 1.3 Definitions
- **TLE:** Two-Line Element set; a satellite orbit snapshot propagated by SGP4.
- **Pass:** an interval a satellite is above a set elevation for an observer.
- **Altitude / Azimuth:** height above the horizon and compass direction.
- **Radiant:** the sky point a meteor shower appears to originate from.
- **ZHR:** zenithal hourly rate; a shower's meteors-per-hour under ideal conditions.
- **Ephemeris:** precomputed Solar-System body positions (JPL DE421) for Sun/Moon.
- **Visible:** for the ISS, dark sky and sunlit station; for a shower, dark sky and
  radiant above the horizon; for a lunar eclipse, Moon above the horizon.

### 1.4 References
CelesTrak orbital elements; JPL DE421 ephemeris; Skyfield (incl. `eclipselib`);
IAU / American Meteor Society shower data; project Decision Log (`docs/decisions.md`).

---

## 2. Overall Description

### 2.1 Product perspective
A Python backend of cooperating parts: an astronomy computation core, a reusable
events service, a relational store, a scheduled ingestion + alert pipeline, and a
FastAPI web layer. A read path computes events on demand for any location; a write
path stores events per subscriber location and drives alerts.

### 2.2 Product functions
Compute events for a location; evaluate visibility; serve events over HTTP; register
subscribers; ingest events per subscriber location on a schedule; email each
subscriber for their location's upcoming visible events without duplicates.

### 2.3 User classes
- **Sky-watcher (subscriber):** registers a location, receives personalized alerts.
- **API consumer:** queries events for any location over HTTP.
- **Operator/developer:** configures credentials, runs the API and scheduler.

### 2.4 Constraints
Python 3.13; SQLite via SQLAlchemy 2.0 (URL configurable via `DATABASE_URL`);
Skyfield for astronomy; free data sources subject to their rate limits and terms;
secrets only in a git-ignored `.env`.

### 2.5 Assumptions and dependencies
Network access for orbital-data refresh and email; the ephemeris is downloaded once
and cached; all datetimes are stored/served as UTC and localized only for display.

---

## 3. Functional Requirements

**FR-1 — Orbital data acquisition.** Fetch the ISS TLE from CelesTrak with a
descriptive User-Agent, not re-downloading data under two hours old.

**FR-2 — Data validation.** Validate fetched data as a well-formed TLE before
overwriting the stored copy; preserve the existing copy on failure.

**FR-3 — ISS pass computation.** Compute rise/peak/set events for a lat/lon over a
window via SGP4, keeping passes above a minimum peak elevation.

**FR-4 — Meteor shower computation.** From curated shower data, compute the peak
night's best viewing moment, radiant altitude, and Moon illumination for a location.

**FR-5 — Lunar eclipse computation.** Compute lunar eclipses in a window and the
Moon's altitude at greatest eclipse for a location.

**FR-6 — Visibility evaluation.** Determine visibility per event type: ISS (dark sky
and sunlit station), shower (dark sky and radiant up), eclipse (Moon above horizon).

**FR-7 — Persistence.** Store events with location, timing, visibility, and
type-specific detail; store subscribers and sent-alert records.

**FR-8 — Idempotent ingestion.** Re-running ingestion for a location must not create
duplicate events.

**FR-9 — Events API.** `GET /events?lat&lon&days` returns upcoming events for any
valid location, computed on demand, sorted by time; invalid coordinates are rejected.

**FR-10 — Subscription API.** `POST /subscribe` registers or updates a subscriber
(email + location); invalid email or coordinates are rejected.

**FR-11 — Per-user alert detection.** For each active subscriber, identify visible
upcoming events at their location within a per-type lead window, not already alerted.

**FR-12 — Alert delivery.** Deliver each due alert to the subscriber's email through a
configurable notifier, with local-time, type-appropriate content.

**FR-13 — Per-user de-duplication.** Never send the same subscriber the same event
twice; dedup is keyed per user so subscribers are independent.

**FR-14 — Scheduling.** Automatically refresh data for all subscriber locations and
run alerting at a fixed interval.

---

## 4. Non-Functional Requirements

**NFR-1 — Accuracy.** Predictions use orbital data no older than the refresh window;
visibility uses real Sun/Moon geometry.

**NFR-2 — Reliability.** External-dependency failures (data source, mail server) must
not corrupt stored data; validation and transactional writes protect integrity.

**NFR-3 — Security.** No credential in source or version control; secrets come from
the environment via a git-ignored `.env`.

**NFR-4 — Maintainability.** The astronomy core is independent of the database, web,
and delivery layers; a service function holds shared logic; behavior is covered by an
automated test suite.

**NFR-5 — Portability.** A configurable database URL and environment-based secrets
allow migration to a server database and hosted environment without logic changes.

**NFR-6 — Input validation.** All API inputs are validated (coordinate ranges, email
format) with clear error responses.

**NFR-7 — Good external-citizenship.** Respect data providers' rate limits and caching
guidance.

---

## 5. External Interface Requirements

- **CelesTrak (HTTPS):** ISS orbital elements; read-only, descriptive User-Agent,
  >=2-hour cache.
- **JPL DE421 ephemeris (file):** Sun/Moon positions; downloaded once, cached.
- **SMTP (Gmail):** outbound alert email over STARTTLS, app-password auth from env.
- **HTTP/REST (FastAPI):** `GET /`, `GET /events`, `POST /subscribe`; interactive docs
  at `/docs`.

---

## 6. Data Model

- **events:** id, event_type, name, latitude, longitude, start_utc, peak_utc, end_utc,
  visible, peak_altitude_deg?, sun_altitude_deg?, iss_sunlit?, details (JSON),
  created_at. (`?` = nullable, used only by ISS passes.)
- **users:** id, email (unique), latitude, longitude, active, created_at.
- **sent_alerts:** id, alert_key (unique, `user{id}:<type>@<peak-to-minute>`), sent_at.

All datetimes are UTC.

---

## 7. Known Limitations
Visibility is judged at the peak/greatest-eclipse instant, not across the whole event;
dedup identity is minute-level; meteor peak dates are approximate annual values; the
scheduler runs as a single foreground process; only lunar (not solar) eclipses are
supported.

---

## 8. Future Scope
Solar eclipses with local circumstances; Moon-phase weighting in a visibility *score*;
a web frontend (location form + rendered event list); hosted deployment with an
always-on scheduler; PostgreSQL migration with schema migrations; push notifications.
