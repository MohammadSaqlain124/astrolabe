from dataclasses import dataclass
from datetime import datetime

from skyfield.api import EarthSatellite, Loader, wgs84

_load = Loader("data")
_ts = _load.timescale()
_eph = _load("de421.bsp")
_sun = _eph["sun"]
_earth = _eph["earth"]

DARK_ENOUGH_DEG = -6.0  # sun this far below the horizon = sky dark enough to spot the ISS


@dataclass
class IssPass:
    start_utc: datetime
    peak_utc: datetime
    end_utc: datetime
    peak_altitude_deg: float
    sun_altitude_deg: float
    iss_sunlit: bool
    visible: bool


def load_tle(path: str) -> tuple[str, str]:
    with open(path) as f:
        lines = [line.strip() for line in f if line.strip()]
    line1 = next(ln for ln in lines if ln.startswith("1 "))
    line2 = next(ln for ln in lines if ln.startswith("2 "))
    return line1, line2


def _sun_altitude_deg(place, t) -> float:
    altitude, _, _ = (_earth + place).at(t).observe(_sun).apparent().altaz()
    return altitude.degrees


def compute_passes(line1, line2, latitude, longitude, start, end, min_altitude=10.0):
    satellite = EarthSatellite(line1, line2, "ISS (ZARYA)", _ts)
    place = wgs84.latlon(latitude, longitude)

    t0, t1 = _ts.from_datetime(start), _ts.from_datetime(end)
    times, events = satellite.find_events(place, t0, t1, altitude_degrees=min_altitude)

    required = {
        "start_utc", "peak_utc", "end_utc",
        "peak_altitude_deg", "sun_altitude_deg", "iss_sunlit", "visible",
    }
    passes, current = [], {}
    for ti, event in zip(times, events):
        moment = ti.utc_datetime()
        if event == 0:
            current = {"start_utc": moment}
        elif event == 1:
            altitude, _, _ = (satellite - place).at(ti).altaz()
            sun_alt = _sun_altitude_deg(place, ti)
            sunlit = bool(satellite.at(ti).is_sunlit(_eph))

            current["peak_utc"] = moment
            current["peak_altitude_deg"] = altitude.degrees
            current["sun_altitude_deg"] = sun_alt
            current["iss_sunlit"] = sunlit
            current["visible"] = sunlit and sun_alt < DARK_ENOUGH_DEG
        elif event == 2:
            current["end_utc"] = moment
            if required <= current.keys():
                passes.append(IssPass(**current))
            current = {}

    return passes