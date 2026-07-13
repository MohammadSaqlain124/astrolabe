from dataclasses import dataclass
from datetime import datetime

from skyfield import eclipselib
from skyfield.api import wgs84

from app.core.sky import earth, eph, moon, ts


@dataclass
class EclipseEvent:
    name: str
    peak_utc: datetime
    visible: bool
    moon_altitude_deg: float


def compute_lunar_eclipses(start, end, latitude, longitude) -> list[EclipseEvent]:
    place = wgs84.latlon(latitude, longitude)
    observer = earth + place

    t0, t1 = ts.from_datetime(start), ts.from_datetime(end)
    times, kinds, _ = eclipselib.lunar_eclipses(t0, t1, eph)

    events = []
    for ti, kind in zip(times, kinds):
        altitude, _, _ = observer.at(ti).observe(moon).apparent().altaz()
        moon_alt = altitude.degrees
        events.append(
            EclipseEvent(
                name=f"{eclipselib.LUNAR_ECLIPSES[kind]} lunar eclipse",
                peak_utc=ti.utc_datetime(),
                visible=bool(moon_alt > 0),
                moon_altitude_deg=float(moon_alt),
            )
        )
    return events