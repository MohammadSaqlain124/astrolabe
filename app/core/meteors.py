import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np
from skyfield import almanac
from skyfield.api import Star, wgs84

from app.core.sky import earth, eph, sun, ts

DARK_ENOUGH_DEG = -12.0  # meteors are faint, so they need a darker sky than the ISS


@dataclass
class ShowerEvent:
    name: str
    start_utc: datetime
    peak_utc: datetime
    end_utc: datetime
    visible: bool
    radiant_altitude_deg: float
    moon_illumination_pct: float
    zhr: int


def load_showers(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)["showers"]


def compute_shower_visibility(shower, year, latitude, longitude) -> ShowerEvent:
    place = wgs84.latlon(latitude, longitude)
    observer = earth + place
    radiant = Star(ra_hours=shower["radiant_ra_hours"], dec_degrees=shower["radiant_dec_deg"])

    # sample every 15 minutes across the ~24 hours of the peak night
    base = datetime(year, shower["peak_month"], shower["peak_day"], 12, tzinfo=timezone.utc)
    moments = [base + timedelta(minutes=15 * i) for i in range(96)]
    t = ts.from_datetimes(moments)

    sun_alt = observer.at(t).observe(sun).apparent().altaz()[0].degrees
    radiant_alt = observer.at(t).observe(radiant).apparent().altaz()[0].degrees
    moon_illum = almanac.fraction_illuminated(eph, "moon", t) * 100

    watchable = (sun_alt < DARK_ENOUGH_DEG) & (radiant_alt > 0)

    if not watchable.any():
        midnight = base + timedelta(hours=12)
        return ShowerEvent(shower["name"], midnight, midnight, midnight,
                           False, float(radiant_alt.max()), float(moon_illum.mean()), shower["zhr"])

    indices = np.where(watchable)[0]
    best = indices[np.argmax(radiant_alt[indices])]

    return ShowerEvent(
        name=shower["name"],
        start_utc=moments[indices[0]],
        peak_utc=moments[best],
        end_utc=moments[indices[-1]],
        visible=True,
        radiant_altitude_deg=float(radiant_alt[best]),
        moon_illumination_pct=float(moon_illum[best]),
        zhr=shower["zhr"],
    )