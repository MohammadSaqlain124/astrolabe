from fastapi import FastAPI, Query
from pydantic import BaseModel, EmailStr, Field

from app.core.database import SessionLocal
from app.core.events_service import upcoming_events
from app.core.models import User

app = FastAPI(title="Astronomy Event Tracker", version="1.0")


class Subscription(BaseModel):
    email: EmailStr
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


@app.get("/")
def root():
    return {"service": "Astronomy Event Tracker", "docs": "/docs"}


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