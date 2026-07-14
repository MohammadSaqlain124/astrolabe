from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, EmailStr, Field

from app.core.database import SessionLocal
from app.core.events_service import upcoming_events
from app.core.models import User

app = FastAPI(title="Astrolabe", version="1.0")

FAVICON = '''<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" fill="none"><circle cx="20" cy="20" r="20" fill="#0B1622"/><circle cx="20" cy="20" r="17.6" stroke="#EAF0F4" stroke-width="1.3"/><circle cx="20" cy="20" r="15.2" stroke="#8298A8" stroke-width="2.2" stroke-dasharray="0.6 2.4"/><circle cx="20" cy="16.8" r="8" stroke="#E8A13C" stroke-width="1.25"/><circle cx="20" cy="20" r="1.4" fill="#EAF0F4"/><path d="M26.6 8.6 L27.45 10.75 L29.6 11.6 L27.45 12.45 L26.6 14.6 L25.75 12.45 L23.6 11.6 L25.75 10.75 Z" fill="#E8A13C"/></svg>'''

STATIC_DIR = Path(__file__).parent / "static"


class Subscription(BaseModel):
    email: EmailStr
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/sky", response_class=HTMLResponse)
def sky():
    return (STATIC_DIR / "sky.html").read_text(encoding="utf-8")


@app.get("/favicon.svg")
def favicon():
    return Response(FAVICON, media_type="image/svg+xml")


@app.get("/events")
def get_events(
    lat: float = Query(..., ge=-90, le=90, description="Latitude in degrees"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude in degrees"),
    days: int = Query(7, ge=1, le=30, description="How many days of ISS passes to include"),
):
    events = upcoming_events(lat, lon, days=days)
    return {"latitude": lat, "longitude": lon, "count": len(events), "events": events}


@app.post("/subscribe")
def subscribe(sub: Subscription):
    with SessionLocal() as session:
        user = session.query(User).filter(User.email == sub.email).first()
        if user:
            user.latitude, user.longitude, user.active = sub.lat, sub.lon, True
            action = "updated"
        else:
            session.add(User(email=sub.email, latitude=sub.lat, longitude=sub.lon))
            action = "created"
        session.commit()
    return {"status": action, "email": sub.email, "lat": sub.lat, "lon": sub.lon}
