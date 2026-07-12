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

### OPEN DECISIONS (to resolve later)

- **Database** (Phase 1): options are MongoDB (author already knows it),
  PostgreSQL + SQLAlchemy (more valuable for a Python backend career), or SQLite
  to start (zero setup, migrate later).
- **Notification channel** (Phase 1): email first (simplest), push later.
