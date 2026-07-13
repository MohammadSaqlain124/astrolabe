from skyfield.api import Loader

load = Loader("data")
ts = load.timescale()
eph = load("de421.bsp")

sun = eph["sun"]
earth = eph["earth"]
moon = eph["moon"]


def sun_altitude_deg(place, t):
    altitude, _, _ = (earth + place).at(t).observe(sun).apparent().altaz()
    return altitude.degrees