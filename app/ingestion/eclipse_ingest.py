from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.core.eclipses import compute_lunar_eclipses
from app.core.models import Event


def ingest_lunar_eclipses(latitude: float, longitude: float, years_ahead: int = 3) -> int:
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=365 * years_ahead)
    eclipses = compute_lunar_eclipses(start, end, latitude, longitude)

    with SessionLocal() as session:
        session.query(Event).filter(
            Event.event_type == "lunar_eclipse",
            Event.latitude == latitude,
            Event.longitude == longitude,
        ).delete()

        for e in eclipses:
            peak = e.peak_utc.replace(tzinfo=None)
            session.add(
                Event(
                    event_type="lunar_eclipse",
                    name=e.name,
                    latitude=latitude,
                    longitude=longitude,
                    start_utc=peak,
                    peak_utc=peak,
                    end_utc=peak,
                    visible=e.visible,
                    details={"moon_altitude_deg": round(e.moon_altitude_deg, 1)},
                )
            )
        session.commit()

    return len(eclipses)


if __name__ == "__main__":
    count = ingest_lunar_eclipses(28.3670, 79.4304)
    print(f"Ingested {count} lunar eclipses for Bareilly.")