"""
Phase 0 spike: predict the next visible-height passes of the ISS over a location.

Goal of this script: prove that the single hardest, riskiest part of the whole
project — turning raw orbital data into "when will the ISS be over MY head" — works
end to end. Everything else in the project is scaffolding around this calculation.

Run:  python scripts/spike_iss_pass.py
"""

from datetime import timezone, timedelta

from skyfield.api import load, wgs84, EarthSatellite

# ---------------------------------------------------------------------------
# 1. THE ORBITAL DATA  (a "TLE" = Two-Line Element set)
# ---------------------------------------------------------------------------
# A TLE is a compact snapshot of a satellite's orbit at one instant in time.
# Those two cryptic lines encode inclination, eccentricity, how fast it circles
# Earth, and — crucially — an EPOCH: the exact moment the snapshot was taken.
# The whole thing is designed to be propagated forward in time by the SGP4
# model to work out where the satellite is at any later moment.
#
# This particular snapshot is from a search result (epoch = 2026, day ~92, i.e.
# early April 2026). We hardcode it here ONLY for the spike. In the real app, a
# scheduled job will fetch a fresh one from CelesTrak, because a TLE is only
# accurate for a few days to ~2 weeks past its epoch (the ISS's orbit decays and
# gets re-boosted, so old data drifts badly). Keep that fact in mind when you
# read the output.
ISS_NAME = "ISS (ZARYA)"
LINE1 = "1 25544U 98067A   26092.84326289  .00011825  00000+0  22447-3 0  9999"
LINE2 = "2 25544  51.6328 312.9475 0006236 264.7845  95.2432 15.48729122560075"

# ---------------------------------------------------------------------------
# 2. TIME  (a Skyfield "timescale")
# ---------------------------------------------------------------------------
# Astronomy needs a very precise notion of time. Skyfield ships built-in time
# data so we don't need network access here.
ts = load.timescale()

# Build the satellite object. This bundles the orbit + the SGP4 propagator.
satellite = EarthSatellite(LINE1, LINE2, ISS_NAME, ts)
print(f"Loaded {satellite}")
print(f"TLE epoch (when this snapshot was taken): {satellite.epoch.utc_strftime('%Y-%m-%d %H:%M UTC')}")

# ---------------------------------------------------------------------------
# 3. THE OBSERVER  (your location on the Earth's surface)
# ---------------------------------------------------------------------------
# wgs84 is the standard model of the Earth's shape used by GPS. We give it a
# latitude and longitude and it knows exactly where you're standing in 3D space.
# These are Bareilly's coordinates — change them to any lat/long later.
LAT, LON = 28.3670, 79.4304          # Bareilly, Uttar Pradesh
place = wgs84.latlon(LAT, LON)
IST = timezone(timedelta(hours=5, minutes=30))   # India Standard Time = UTC+5:30

# ---------------------------------------------------------------------------
# 4. FIND THE PASSES
# ---------------------------------------------------------------------------
# We ask: over the next 3 days, when does the ISS rise above 10 degrees of
# elevation (the horizon plus a bit, since buildings/haze block the very bottom),
# reach its highest point, and set again? find_events returns those three event
# types for every pass in the window.
t0 = ts.utc(2026, 7, 12)      # window start (today)
t1 = ts.utc(2026, 7, 15)      # window end (+3 days)
times, events = satellite.find_events(place, t0, t1, altitude_degrees=10.0)

EVENT_LABEL = {0: "rises above 10 deg", 1: "peaks (highest point)", 2: "sets below 10 deg"}

print(f"\nUpcoming ISS passes over ({LAT}, {LON}) — times in IST:\n")

for ti, event in zip(times, events):
    local = ti.astimezone(IST)
    label = EVENT_LABEL[event]

    # For each event, also compute WHERE in the sky the ISS is:
    #   altitude = how high above the horizon (degrees)
    #   azimuth  = compass direction (0=N, 90=E, 180=S, 270=W)
    topocentric = (satellite - place).at(ti)
    alt, az, distance = topocentric.altaz()

    print(f"  {local.strftime('%a %d %b  %H:%M:%S')}  "
          f"| {label:<20} "
          f"| alt {alt.degrees:5.1f} deg  az {az.degrees:5.1f} deg  "
          f"| range {distance.km:6.0f} km")

print("\nDone. Each 'peak' line is the best moment to look up during that pass.")
