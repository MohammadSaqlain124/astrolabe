from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.core.models import Event, SentAlert, User

IST = timezone(timedelta(hours=5, minutes=30))

LEAD_DAYS = {
    "iss_pass": 1,
    "meteor_shower": 3,
    "lunar_eclipse": 3,
}


def _alert_key(user_id: int, event: Event) -> str:
    return f"user{user_id}:{event.event_type}@{event.peak_utc:%Y-%m-%dT%H:%M}"


def _format_alert(event: Event) -> tuple[str, str]:
    peak_ist = event.peak_utc.replace(tzinfo=timezone.utc).astimezone(IST)
    when = f"{peak_ist:%A, %d %B %Y} at {peak_ist:%H:%M} IST"
    d = event.details or {}

    if event.event_type == "iss_pass":
        subject = f"Visible ISS pass on {peak_ist:%a %d %b} at {peak_ist:%H:%M} IST"
        body = (
            "The International Space Station will be visible from your location.\n\n"
            f"When:        {when}\n"
            f"Peak height: {event.peak_altitude_deg:.0f} degrees above the horizon\n\n"
            "Head outside a few minutes early and let your eyes adjust to the dark."
        )
    elif event.event_type == "meteor_shower":
        moon = d.get("moon_illumination_pct", 0)
        moon_note = "bright, so fainter meteors will be washed out" if moon > 50 else "favourable"
        subject = f"{event.name} meteor shower peaks {peak_ist:%a %d %b}"
        body = (
            f"The {event.name} meteor shower is near its peak.\n\n"
            f"Best time: {when}\n"
            f"Rate:      up to {d.get('zhr', '?')} meteors per hour\n"
            f"Moon:      {moon:.0f}% lit ({moon_note})\n\n"
            "Find a dark spot away from city lights and look up. No telescope needed."
        )
    elif event.event_type == "lunar_eclipse":
        subject = f"{event.name} on {peak_ist:%a %d %b}"
        body = (
            f"A {event.name.lower()} will be visible from your location.\n\n"
            f"Greatest eclipse: {when}\n"
            f"Moon height:      {d.get('moon_altitude_deg', 0):+.0f} degrees above the horizon\n\n"
            "The Moon stays above your horizon during the eclipse. Just look up."
        )
    else:
        subject = f"Upcoming event: {event.name}"
        body = f"{event.name}\nWhen: {when}"

    return subject, body


def check_and_send_alerts(notifier) -> int:
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    sent = 0
    with SessionLocal() as session:
        users = session.query(User).filter(User.active.is_(True)).all()

        for user in users:
            upcoming = (
                session.query(Event)
                .filter(
                    Event.visible.is_(True),
                    Event.peak_utc > now,
                    Event.latitude == user.latitude,
                    Event.longitude == user.longitude,
                )
                .order_by(Event.peak_utc)
                .all()
            )

            for event in upcoming:
                lead = LEAD_DAYS.get(event.event_type, 1)
                if event.peak_utc > now + timedelta(days=lead):
                    continue
                key = _alert_key(user.id, event)
                if session.query(SentAlert).filter(SentAlert.alert_key == key).first():
                    continue
                subject, body = _format_alert(event)
                notifier.send(subject, body, user.email)
                session.add(SentAlert(alert_key=key))
                sent += 1

        session.commit()

    return sent


if __name__ == "__main__":
    from app.alerts.notifier import ConsoleNotifier

    count = check_and_send_alerts(ConsoleNotifier())
    print(f"{count} new alert(s) sent.")