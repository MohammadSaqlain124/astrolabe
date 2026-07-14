from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from app.alerts.engine import check_and_send_alerts
from app.alerts.notifier import EmailNotifier
from app.core.database import SessionLocal
from app.core.models import User
from app.ingestion.eclipse_ingest import ingest_lunar_eclipses
from app.ingestion.iss_ingest import ingest_iss_passes
from app.ingestion.meteor_ingest import ingest_meteor_showers
from app.ingestion.tle_fetch import fetch_tle


def refresh_and_alert(notifier):
    fetch_tle()

    with SessionLocal() as session:
        locations = {
            (u.latitude, u.longitude)
            for u in session.query(User).filter(User.active.is_(True)).all()
        }

    for lat, lon in locations:
        ingest_iss_passes(lat, lon)
        ingest_meteor_showers(lat, lon)
        ingest_lunar_eclipses(lat, lon)

    sent = check_and_send_alerts(notifier)
    print(f"Refresh complete: {len(locations)} location(s), {sent} alert(s) emailed.")


def main():
    load_dotenv()
    notifier = EmailNotifier()

    refresh_and_alert(notifier)

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(refresh_and_alert, "interval", hours=2, args=[notifier], id="refresh")
    print("Scheduler running: refresh + alerts every 2 hours. Press Ctrl+C to stop.")
    scheduler.start()


if __name__ == "__main__":
    main()