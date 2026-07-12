from datetime import timedelta, timezone

from app.core.database import SessionLocal
from app.core.models import Event

IST = timezone(timedelta(hours=5, minutes=30))


def main():
    with SessionLocal() as session:
        passes = (
            session.query(Event)
            .filter(Event.event_type == "iss_pass")
            .order_by(Event.peak_utc)
            .all()
        )

    visible = [p for p in passes if p.visible]
    print(f"{len(passes)} passes total, {len(visible)} visible (times in IST):\n")
    print(f"  {'':<7} {'peak (IST)':<16} {'max alt':>7} {'sun alt':>8} {'ISS lit':>8}")
    for p in passes:
        peak_ist = p.peak_utc.replace(tzinfo=timezone.utc).astimezone(IST)
        peak_str = peak_ist.strftime("%a %d %b %H:%M")
        marker = "VISIBLE" if p.visible else ""
        lit = "yes" if p.iss_sunlit else "no"
        print(
            f"  {marker:<7} {peak_str:<16} "
            f"{p.peak_altitude_deg:6.0f}° {p.sun_altitude_deg:7.0f}° {lit:>8}"
        )


if __name__ == "__main__":
    main()