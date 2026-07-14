from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.eclipses import compute_lunar_eclipses
from app.core.iss import compute_passes, load_tle
from app.core.meteors import compute_shower_visibility, load_showers
from app.ingestion.tle_fetch import fetch_tle

TLE_FILE = "data/iss_tle.txt"
SHOWER_FILE = "data/meteor_showers.json"


def upcoming_events(latitude: float, longitude: float, days: int = 7) -> list[dict]:
    now = datetime.now(timezone.utc)
    events: list[dict] = []

    # ISS passes need current orbital data. On a fresh server that file won't exist
    # yet, so fetch it on demand; if it's still unavailable, skip ISS rather than fail.
    try:
        if not Path(TLE_FILE).exists():
            fetch_tle()
        line1, line2 = load_tle(TLE_FILE)
        for p in compute_passes(line1, line2, latitude, longitude, now, now + timedelta(days=days)):
            events.append({
                "type": "iss_pass",
                "name": "ISS pass",
                "peak_utc": p.peak_utc.isoformat(),
                "visible": bool(p.visible),
                "details": {
                    "peak_altitude_deg": round(float(p.peak_altitude_deg), 1),
                    "sun_altitude_deg": round(float(p.sun_altitude_deg), 1),
                    "iss_sunlit": bool(p.iss_sunlit),
                },
            })
    except Exception as exc:
        print("ISS passes unavailable:", exc)

    for shower in load_showers(SHOWER_FILE):
        peak_date = datetime(now.year, shower["peak_month"], shower["peak_day"], tzinfo=timezone.utc)
        year = now.year if peak_date >= now else now.year + 1
        e = compute_shower_visibility(shower, year, latitude, longitude)
        events.append({
            "type": "meteor_shower",
            "name": e.name,
            "peak_utc": e.peak_utc.isoformat(),
            "visible": bool(e.visible),
            "details": {
                "zhr": e.zhr,
                "radiant_altitude_deg": round(float(e.radiant_altitude_deg), 1),
                "moon_illumination_pct": round(float(e.moon_illumination_pct), 1),
            },
        })

    for e in compute_lunar_eclipses(now, now + timedelta(days=730), latitude, longitude):
        events.append({
            "type": "lunar_eclipse",
            "name": e.name,
            "peak_utc": e.peak_utc.isoformat(),
            "visible": bool(e.visible),
            "details": {"moon_altitude_deg": round(float(e.moon_altitude_deg), 1)},
        })

    events.sort(key=lambda ev: ev["peak_utc"])
    return events
