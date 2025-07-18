import datetime as dt
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .base import Base


class SessionDetail(Base):
    __tablename__ = "session_detail"
    id: Mapped[int] = mapped_column(primary_key=True)
    fk_sample_id: Mapped[int] = mapped_column(unique=True)
    ambient_start_at: Mapped[dt.datetime]
    ambient_end_at: Mapped[dt.datetime]
    temp_min: Mapped[float]
    temp_max: Mapped[float]
    temp_mean: Mapped[float]
    precipitation_min: Mapped[float] = mapped_column(nullable=True)
    precipitation_max: Mapped[float] = mapped_column(nullable=True)
    precipitation_mean: Mapped[float] = mapped_column(nullable=True)
    rel_hum_min: Mapped[int]
    rel_hum_max: Mapped[int]
    rel_hum_mean: Mapped[int]
    wind_speed_min: Mapped[float]
    wind_speed_max: Mapped[float]
    wind_speed_mean: Mapped[float]
    wind_dir_mean: Mapped[float]
    weather_condition_code: Mapped[int]

    created_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.now
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.now, onupdate=dt.datetime.now
    )

    def __repr__(self) -> str:
        return f"SessionDetail(specie={self.fk_sample_id})"
