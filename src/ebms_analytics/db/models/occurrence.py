import datetime as dt
from sqlalchemy import TIMESTAMP, FetchedValue
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .base import Base


class Occurrence(Base):
    __tablename__ = "ocurrence"
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int]
    occurrence_id: Mapped[int] = mapped_column(unique=True)
    location: Mapped[str]
    location_id: Mapped[int]
    country: Mapped[str] = mapped_column(String(50))
    date: Mapped[dt.date]
    recorder_name: Mapped[str]
    identified_by: Mapped[str]
    accepted_species_name: Mapped[str]
    authority: Mapped[str]
    family: Mapped[str]
    verification_status: Mapped[bool] = mapped_column(default=False)
    verified_by: Mapped[str] = mapped_column(nullable=True)
    count_inside: Mapped[int] = mapped_column(default=0)
    count_outside: Mapped[int] = mapped_column(default=0)
    count: Mapped[int] = mapped_column(server_default=FetchedValue())
    latitude_full: Mapped[str]
    longitude_full: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    record_status: Mapped[str] = mapped_column(String(50))
    record_substatus: Mapped[str] = mapped_column(String(50))
    comments: Mapped[str] = mapped_column(nullable=True)
    occurrence_comment: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.now
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.now, onupdate=dt.datetime.now
    )

    def __repr__(self) -> str:
        return f"Occurence(specie={self.accepted_species_name}, date={self.date.isoformat()}, location={self.location})"
