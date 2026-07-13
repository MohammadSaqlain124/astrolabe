from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from app.alerts.engine import check_and_send_alerts
from app.alerts.notifier import EmailNotifier
from app.ingestion.iss_ingest import ingest_iss_passes
from app.ingestion.tle_fetch import fetch_tle

LOCATION = (28.3670, 79.4304)  # Bareilly


def refresh_and_alert(notifier):
    fetch_tle()
    count = ingest_iss_passes(*LOCATION)
    sent = check_and_send_alerts(notifier, within_hours=24)
    print(f"Refresh complete: {count} passes stored, {sent} alert(s) emailed.")


def main():
    load_dotenv()
    notifier = EmailNotifier()

    refresh_and_alert(notifier)

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(refresh_and_alert, "interval", hours=2, args=[notifier], id="iss_refresh")
    print("Scheduler running: refresh + alerts every 2 hours. Press Ctrl+C to stop.")
    scheduler.start()


if __name__ == "__main__":
    main()