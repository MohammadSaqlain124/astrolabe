from datetime import datetime, timezone

from sqlalchemy import String
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
    peak_altitude_deg: Mapped[float]
    sun_altitude_deg: Mapped[float]
    iss_sunlit: Mapped[bool]
    visible: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    def __repr__(self) -> str:
        return (
            f"<Event {self.event_type} peak={self.peak_utc:%Y-%m-%d %H:%M} "
            f"alt={self.peak_altitude_deg:.0f}deg>"
        )

class SentAlert(Base):
    __tablename__ = "sent_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_key: Mapped[str] = mapped_column(String(80), unique=True)
    sent_at: Mapped[datetime] = mapped_column(default=_utcnow)