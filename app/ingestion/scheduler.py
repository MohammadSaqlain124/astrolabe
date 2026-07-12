from apscheduler.schedulers.blocking import BlockingScheduler

from app.ingestion.iss_ingest import ingest_iss_passes
from app.ingestion.tle_fetch import fetch_tle

LOCATION = (28.3670, 79.4304)  # Bareilly


def refresh():
    fetch_tle()
    count = ingest_iss_passes(*LOCATION)
    print(f"Refresh complete: {count} passes stored.")


def main():
    refresh()

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(refresh, "interval", hours=2, id="iss_refresh")
    print("Scheduler running. Refreshing every 2 hours. Press Ctrl+C to stop.")
    scheduler.start()


if __name__ == "__main__":
    main()