import datetime as dt
from sqlalchemy import TIMESTAMP
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .base import Base


class EbmsOccurrence(Base):
    __tablename__ = "ebms_occurrence"
    id: Mapped[int] = mapped_column(primary_key=True)
    occurrence_key: Mapped[str] = mapped_column(unique=True)
    location_id: Mapped[int]
    location: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[dt.date]
    recorded_by: Mapped[str]
    identified_by: Mapped[str] = mapped_column(nullable=True)
    validated_by: Mapped[str] = mapped_column(nullable=True)
    validation_status: Mapped[str] = mapped_column(String(5))
    release_status: Mapped[str] = mapped_column(String(5))
    family: Mapped[str]
    subfamily: Mapped[str] = mapped_column(nullable=True)
    genus: Mapped[str] = mapped_column(nullable=True)
    epithet: Mapped[str] = mapped_column(nullable=True)
    species: Mapped[str] = mapped_column(nullable=True)
    species_name: Mapped[str] = mapped_column(nullable=True)
    life_stage: Mapped[str] = mapped_column(String(100), nullable=True)
    count: Mapped[int] = mapped_column(default=0)
    latitude: Mapped[float]
    longitude: Mapped[float]
    species_authorship: Mapped[str] = mapped_column(nullable=True)
    year: Mapped[int]
    month: Mapped[int]
    taxon_rank: Mapped[str] = mapped_column(String(10), nullable=True)
    event_id: Mapped[int]

    # country: Mapped[str] = mapped_column(nullable=True)
    # province: Mapped[str] = mapped_column(nullable=True)
    # county: Mapped[str] = mapped_column(nullable=True)
    # municipality: Mapped[str] = mapped_column(nullable=True)
    # locality: Mapped[str] = mapped_column(nullable=True)
    # country_code: Mapped[str] = mapped_column(String(5), default='PT')

    # trap: Mapped[str] = mapped_column(nullable=True)
    # event_time: Mapped[str] = mapped_column(String(100), nullable=True)
    # event_start_time: Mapped[str] = mapped_column(String(20), nullable=True)
    # event_end_time: Mapped[str] = mapped_column(String(20), nullable=True)
    # sampling_effort: Mapped[str] = mapped_column(String(100), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.now
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.now, onupdate=dt.datetime.now
    )

    def __repr__(self) -> str:
        return f"EBMS Occurence(name={self.name}, date={self.date.isoformat()}, location={self.location_id})"
