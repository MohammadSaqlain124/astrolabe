from datetime import datetime

from app.core.database import SessionLocal
from app.core.models import Event


def main():
    with SessionLocal() as session:
        fake = Event(
            event_type="iss_pass",
            name="ISS pass",
            latitude=28.3670,
            longitude=79.4304,
            start_utc=datetime(2026, 7, 14, 2, 11, 50),
            peak_utc=datetime(2026, 7, 14, 2, 15, 10),
            end_utc=datetime(2026, 7, 14, 2, 18, 30),
            peak_altitude_deg=86.0,
        )
        session.add(fake)
        session.commit()

        events = session.query(Event).all()
        print(f"{len(events)} event(s) in the database:")
        for e in events:
            print(" ", e)


if __name__ == "__main__":
    main()