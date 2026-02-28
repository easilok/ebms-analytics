import datetime as dt
from sqlalchemy import TIMESTAMP, FetchedValue
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .base import Base


class GbifOccurrence(Base):
    __tablename__ = "gbif_occurrence"
    id: Mapped[int] = mapped_column(primary_key=True)
    occurrence_key: Mapped[str] = mapped_column(unique=True)
    location_id: Mapped[int]
    location: Mapped[str] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column(nullable=True)
    province: Mapped[str] = mapped_column(nullable=True)
    county: Mapped[str] = mapped_column(nullable=True)
    municipality: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[dt.date]
    # recorded_by: Mapped[list[str]] = mapped_column(default=[])
    # identified_by: Mapped[list[str]] = mapped_column(default=[])
    species: Mapped[str] = mapped_column(nullable=True)
    genus: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    family: Mapped[str]
    life_stage: Mapped[str] = mapped_column(String(100), nullable=True)
    count: Mapped[int] = mapped_column(default=0)
    latitude: Mapped[float]
    longitude: Mapped[float]
    trap: Mapped[str] = mapped_column(nullable=True)
    event_time: Mapped[str] = mapped_column(String(100), nullable=True)
    event_start_time: Mapped[str] = mapped_column(String(20), nullable=True)
    event_end_time: Mapped[str] = mapped_column(String(20), nullable=True)
    name_authorship: Mapped[str] = mapped_column(String(150), nullable=True)
    year: Mapped[int] = mapped_column(server_default=FetchedValue())
    month: Mapped[int] = mapped_column(server_default=FetchedValue())
    session_id: Mapped[int] = mapped_column(server_default=FetchedValue())
    locality: Mapped[str] = mapped_column(nullable=True)
    country_code: Mapped[str] = mapped_column(String(5), default='PT')
    taxon_rank: Mapped[str] = mapped_column(String(10), nullable=True)
    sampling_effort: Mapped[str] = mapped_column(String(100), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.now
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.now, onupdate=dt.datetime.now
    )

    def __repr__(self) -> str:
        return f"GBIF Occurence(name={self.name}, date={self.date.isoformat()}, location={self.location_id})"
