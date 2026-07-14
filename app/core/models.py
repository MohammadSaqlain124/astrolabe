from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[float]
    longitude: Mapped[float]
    start_utc: Mapped[datetime]
    peak_utc: Mapped[datetime]
    end_utc: Mapped[datetime]
    visible: Mapped[bool]

    # ISS-specific (null for other event types)
    peak_altitude_deg: Mapped[Optional[float]]
    sun_altitude_deg: Mapped[Optional[float]]
    iss_sunlit: Mapped[Optional[bool]]

    # per-type extra data (radiant altitude, ZHR, moon %, ...)
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    def __repr__(self) -> str:
        return f"<Event {self.event_type} {self.name} peak={self.peak_utc:%Y-%m-%d %H:%M}>"

class SentAlert(Base):
    __tablename__ = "sent_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_key: Mapped[str] = mapped_column(String(80), unique=True)
    sent_at: Mapped[datetime] = mapped_column(default=_utcnow)
    
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)