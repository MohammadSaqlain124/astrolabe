from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.core.models import Event, SentAlert

IST = timezone(timedelta(hours=5, minutes=30))


def _alert_key(peak_utc: datetime) -> str:
    return f"iss_pass@{peak_utc:%Y-%m-%dT%H:%M}"


def _format_alert(peak_utc: datetime, peak_altitude_deg: float) -> tuple[str, str]:
    peak_ist = peak_utc.replace(tzinfo=timezone.utc).astimezone(IST)
    subject = f"Visible ISS pass on {peak_ist:%a %d %b} at {peak_ist:%H:%M} IST"
    body = (
        "The International Space Station will be visible from your location.\n\n"
        f"When:        {peak_ist:%A, %d %B %Y} at {peak_ist:%H:%M} IST\n"
        f"Peak height: {peak_altitude_deg:.0f}° above the horizon\n\n"
        "Head outside a few minutes early and let your eyes adjust to the dark."
    )
    return subject, body


def check_and_send_alerts(notifier, within_hours: int = 24) -> int:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    horizon = now + timedelta(hours=within_hours)

    sent = 0
    with SessionLocal() as session:
        upcoming = (
            session.query(Event)
            .filter(
                Event.event_type == "iss_pass",
                Event.visible.is_(True),
                Event.peak_utc > now,
                Event.peak_utc <= horizon,
            )
            .order_by(Event.peak_utc)
            .all()
        )

        for p in upcoming:
            key = _alert_key(p.peak_utc)
            if session.query(SentAlert).filter(SentAlert.alert_key == key).first():
                continue
            subject, body = _format_alert(p.peak_utc, p.peak_altitude_deg)
            notifier.send(subject, body)
            session.add(SentAlert(alert_key=key))
            sent += 1

        session.commit()

    return sent


if __name__ == "__main__":
    from app.alerts.notifier import ConsoleNotifier

    count = check_and_send_alerts(ConsoleNotifier())
    print(f"{count} new alert(s) sent.")