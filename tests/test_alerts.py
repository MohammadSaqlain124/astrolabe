from datetime import datetime, timedelta, timezone

from app.alerts.engine import check_and_send_alerts
from app.core.database import SessionLocal
from app.core.models import Event, User


class CaptureNotifier:
    def __init__(self):
        self.sent = []

    def send(self, subject, body, recipient):
        self.sent.append((recipient, subject))


def _event(lat, lon, peak):
    return Event(event_type="iss_pass", name="ISS pass", latitude=lat, longitude=lon,
                 visible=True, peak_altitude_deg=70.0, sun_altitude_deg=-12.0, iss_sunlit=True,
                 details={}, start_utc=peak, peak_utc=peak, end_utc=peak)


def test_per_user_routing_and_dedup():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with SessionLocal() as s:
        s.add_all([User(email="a@x.com", latitude=10.0, longitude=10.0),
                   User(email="b@x.com", latitude=20.0, longitude=20.0)])
        s.add(_event(10.0, 10.0, now + timedelta(hours=6)))
        s.add(_event(20.0, 20.0, now + timedelta(hours=6)))
        s.commit()

    notifier = CaptureNotifier()
    assert check_and_send_alerts(notifier) == 2
    assert {r for r, _ in notifier.sent} == {"a@x.com", "b@x.com"}
    assert check_and_send_alerts(CaptureNotifier()) == 0  # dedup on second run


def test_lead_time_filters_far_events():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with SessionLocal() as s:
        s.add(User(email="c@x.com", latitude=30.0, longitude=30.0))
        s.add(_event(30.0, 30.0, now + timedelta(days=5)))  # beyond ISS 1-day lead
        s.commit()
    assert check_and_send_alerts(CaptureNotifier()) == 0
