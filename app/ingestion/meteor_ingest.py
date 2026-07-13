from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.core.meteors import compute_shower_visibility, load_showers
from app.core.models import Event

SHOWER_FILE = "data/meteor_showers.json"


def _next_occurrence_year(shower, now: datetime) -> int:
    this_year_peak = datetime(now.year, shower["peak_month"], shower["peak_day"], tzinfo=timezone.utc)
    return now.year if this_year_peak >= now else now.year + 1


def ingest_meteor_showers(latitude: float, longitude: float) -> int:
    showers = load_showers(SHOWER_FILE)
    now = datetime.now(timezone.utc)

    with SessionLocal() as session:
        session.query(Event).filter(
            Event.event_type == "meteor_shower",
            Event.latitude == latitude,
            Event.longitude == longitude,
        ).delete()

        for shower in showers:
            year = _next_occurrence_year(shower, now)
            e = compute_shower_visibility(shower, year, latitude, longitude)
            session.add(
                Event(
                    event_type="meteor_shower",
                    name=e.name,
                    latitude=latitude,
                    longitude=longitude,
                    start_utc=e.start_utc.replace(tzinfo=None),
                    peak_utc=e.peak_utc.replace(tzinfo=None),
                    end_utc=e.end_utc.replace(tzinfo=None),
                    visible=e.visible,
                    details={
                        "zhr": e.zhr,
                        "radiant_altitude_deg": round(e.radiant_altitude_deg, 1),
                        "moon_illumination_pct": round(e.moon_illumination_pct, 1),
                    },
                )
            )
        session.commit()

    return len(showers)


if __name__ == "__main__":
    count = ingest_meteor_showers(28.3670, 79.4304)
    print(f"Ingested {count} meteor showers for Bareilly.")