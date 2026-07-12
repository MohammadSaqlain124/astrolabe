import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
TLE_FILE = Path("data/iss_tle.txt")
MAX_AGE = timedelta(hours=2)
USER_AGENT = "astronomy-tracker/0.1 (student project; your-email@example.com)"


def _is_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return datetime.now(timezone.utc) - modified < MAX_AGE


def _looks_like_tle(text: str) -> bool:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    has_line1 = any(ln.startswith("1 ") for ln in lines)
    has_line2 = any(ln.startswith("2 ") for ln in lines)
    return has_line1 and has_line2


def fetch_tle(url: str = TLE_URL, path: Path = TLE_FILE, force: bool = False) -> bool:
    if not force and _is_fresh(path):
        print("TLE is fresh (< 2h old); skipping download to respect CelesTrak's limits.")
        return False

    response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()

    if not _looks_like_tle(response.text):
        raise ValueError("Downloaded data is not a valid TLE; keeping the existing file.")

    path.write_text(response.text.strip() + "\n")
    print(f"Fetched fresh TLE and saved to {path}.")
    return True
if __name__ == "__main__":
    fetch_tle(force="--force" in sys.argv)