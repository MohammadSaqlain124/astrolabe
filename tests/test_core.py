from datetime import datetime, timedelta, timezone

from app.core.eclipses import compute_lunar_eclipses
from app.core.events_service import upcoming_events
from app.core.iss import IssPass, compute_passes, load_tle
from app.core.meteors import compute_shower_visibility, load_showers


def test_load_tle_returns_two_lines():
    l1, l2 = load_tle("data/iss_tle.txt")
    assert l1.startswith("1 ") and l2.startswith("2 ")


def test_passes_are_ordered_and_typed():
    l1, l2 = load_tle("data/iss_tle.txt")
    now = datetime.now(timezone.utc)
    passes = compute_passes(l1, l2, 28.36, 79.43, now, now + timedelta(days=3))
    for p in passes:
        assert isinstance(p, IssPass)
        assert p.start_utc <= p.peak_utc <= p.end_utc
        assert p.peak_altitude_deg >= 10.0


def test_meteor_fields_in_range():
    showers = load_showers("data/meteor_showers.json")
    e = compute_shower_visibility(showers[0], 2027, 28.36, 79.43)
    assert e.zhr > 0
    assert -90 <= e.radiant_altitude_deg <= 90
    assert 0 <= e.moon_illumination_pct <= 100


def test_eclipse_visibility_is_location_dependent():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2029, 6, 1, tzinfo=timezone.utc)
    verdicts = {e.visible for e in compute_lunar_eclipses(t0, t1, 28.36, 79.43)}
    assert True in verdicts and False in verdicts  # some visible, some not


def test_events_service_sorted_and_native_types():
    events = upcoming_events(28.36, 79.43, days=3)
    assert events == sorted(events, key=lambda e: e["peak_utc"])
    for e in events:
        assert isinstance(e["visible"], bool)  # native python, not numpy
        assert e["type"] in {"iss_pass", "meteor_shower", "lunar_eclipse"}
