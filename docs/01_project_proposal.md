# Project Proposal / Synopsis

**Project title:** Astronomy Event Tracker with Personalized Alerts
**Author:** Mohd. Saqlain Hussain
**Date started:** 2026-07-12

## 1. Problem statement

Astronomy apps and websites list celestial events (meteor showers, eclipses, ISS
passes) as things that happen "somewhere on Earth," leaving the user to work out
whether an event is visible from their own location, at a dark enough hour, without
the Moon washing it out. Casual sky-watchers miss events they could have seen
because no tool answers the specific question: *"What can I actually see from where
I am, and when should I look up?"*

## 2. Objective

Build a backend service that, for a given latitude/longitude:

1. Aggregates upcoming celestial events from multiple sources on a schedule.
2. Computes, per event, whether it is genuinely observable from that location —
   accounting for the horizon, astronomical twilight (darkness), and Moon
   interference.
3. Sends personalized alerts ahead of visible events.

## 3. Scope

**In scope (v1):**
- ISS pass prediction from orbital data (computed locally).
- Meteor shower and eclipse visibility from curated + computed data.
- Per-location visibility scoring (horizon + twilight + moon phase).
- Scheduled data ingestion.
- Alert delivery (email to start).
- A simple frontend showing "what's visible tonight."

**Out of scope (v1):** telescope control, deep-sky object catalogs, social features,
mobile apps.

## 4. Technology

Python throughout. Skyfield for astronomy (satellite propagation and sun/moon/
twilight), FastAPI for the web API, APScheduler for scheduled jobs. Database chosen
in Phase 1.

## 5. Data sources

| Event type      | Source                                   | Notes |
|-----------------|------------------------------------------|-------|
| ISS passes      | CelesTrak orbital elements (TLE) + SGP4  | Refresh every few hours; data goes stale within ~2 weeks |
| Sun / Moon      | Skyfield + JPL ephemeris (computed)      | No external API, no rate limit |
| Eclipses        | USNO API / curated NASA eclipse data     | |
| Meteor showers  | Curated dataset (IAU / American Meteor Society) | Seeded once into the DB |

*(A fuller data-source inventory with rate limits and licenses is maintained in a
separate document.)*

## 6. Success criteria

- Given a location and date, the system returns the next N visible events with
  accurate times, directions, and a visibility rating.
- Alerts fire ahead of visible events without duplicates.
- Predictions for the ISS use orbital data no older than the refresh window.

## 7. Known risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Stale orbital data (TLE past epoch) | Wrong ISS predictions | Scheduled refresh; reject data older than N days |
| External API deprecated/blocked | Missing event data | Compute locally where possible; cache in DB; respect robots/rate limits |
| Timezone / UTC handling bugs | Alerts fire at wrong local time | Store everything in UTC; convert only at display |

## 8. Milestones

| Phase | Deliverable |
|-------|-------------|
| 0 | Spike: compute an ISS pass for a location *(done)* |
| 1 | MVP: scheduled ISS ingestion + one working alert |
| 2 | Full visibility engine + meteor showers + eclipses |
| 3 | FastAPI + frontend + deployment + final report |
