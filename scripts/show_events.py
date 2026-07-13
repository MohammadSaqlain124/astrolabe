from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.core.models import Event

IST = timezone(timedelta(hours=5, minutes=30))


def main():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with SessionLocal() as session:
        events = (
            session.query(Event)
            .filter(Event.peak_utc > now)
            .order_by(Event.peak_utc)
            .all()
        )

    print(f"{len(events)} upcoming events (times in IST):\n")
    for e in events:
        peak = e.peak_utc.replace(tzinfo=timezone.utc).astimezone(IST)
        marker = "VISIBLE" if e.visible else ""
        line = f"  {marker:<7} {peak:%a %d %b %Y %H:%M}  {e.name}"
        d = e.details or {}
        if e.event_type == "iss_pass":
            line += f"  — ISS pass, max alt {e.peak_altitude_deg:.0f}°"
        elif e.event_type == "meteor_shower":
            line += (f"  — meteor shower, ZHR {d.get('zhr', '?')}, "
                     f"radiant {d.get('radiant_altitude_deg', 0):.0f}°, "
                     f"moon {d.get('moon_illumination_pct', 0):.0f}% lit")
        elif e.event_type == "lunar_eclipse":
            line += f"  — moon {d.get('moon_altitude_deg', 0):+.0f}° at greatest eclipse"
        print(line)


if __name__ == "__main__":
    main()