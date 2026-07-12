from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.core.iss import compute_passes, load_tle
from app.core.models import Event

TLE_FILE = "data/iss_tle.txt"


def ingest_iss_passes(latitude: float, longitude: float, days: int = 7) -> int:
    line1, line2 = load_tle(TLE_FILE)

    start = datetime.now(timezone.utc)
    end = start + timedelta(days=days)
    passes = compute_passes(line1, line2, latitude, longitude, start, end)

    with SessionLocal() as session:
        session.query(Event).filter(
            Event.event_type == "iss_pass",
            Event.latitude == latitude,
            Event.longitude == longitude,
        ).delete()

        for p in passes:
            session.add(
                Event(
                    event_type="iss_pass",
                    name="ISS pass",
                    latitude=latitude,
                    longitude=longitude,
                    start_utc=p.start_utc,
                    peak_utc=p.peak_utc,
                    end_utc=p.end_utc,
                    peak_altitude_deg=p.peak_altitude_deg,
                    sun_altitude_deg=p.sun_altitude_deg,
                    iss_sunlit=p.iss_sunlit,
                    visible=p.visible,
                )
            )
        session.commit()

    return len(passes)


if __name__ == "__main__":
    count = ingest_iss_passes(28.3670, 79.4304)
    print(f"Ingested {count} ISS passes for Bareilly.")