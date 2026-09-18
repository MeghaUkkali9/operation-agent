import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class VesselStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ARRIVED = "arrived"
    DEPARTED = "departed"
    DELAYED = "delayed"


class ContainerType(str, enum.Enum):
    STANDARD = "standard"
    REEFER = "reefer"
    DANGEROUS_GOODS = "dangerous_goods"
    OPEN_TOP = "open_top"
    FLAT_RACK = "flat_rack"


class ContainerStatus(str, enum.Enum):
    IN_YARD = "in_yard"
    LOADED = "loaded"
    DISPATCHED = "dispatched"
    DELAYED = "delayed"
    DAMAGED = "damaged"


class Priority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


def db_enum(enum_cls: type[enum.Enum], name: str) -> Enum:
    # store the lowercase .value ("delayed"), not the .name ("DELAYED") SQLAlchemy defaults to
    return Enum(enum_cls, name=name, values_callable=lambda obj: [e.value for e in obj])


class Vessel(Base):
    __tablename__ = "vessels"

    id: Mapped[int] = mapped_column(primary_key=True)
    vessel_name: Mapped[str] = mapped_column(String(100), index=True)
    voyage_number: Mapped[str] = mapped_column(String(20))
    arrival_date: Mapped[date] = mapped_column(Date)
    departure_date: Mapped[date] = mapped_column(Date)
    status: Mapped[VesselStatus] = mapped_column(db_enum(VesselStatus, "vessel_status"))
    terminal: Mapped[str] = mapped_column(String(50))

    containers: Mapped[list["Container"]] = relationship(back_populates="vessel")


class Container(Base):
    __tablename__ = "containers"

    id: Mapped[int] = mapped_column(primary_key=True)
    container_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"), index=True)
    container_type: Mapped[ContainerType] = mapped_column(db_enum(ContainerType, "container_type"))
    status: Mapped[ContainerStatus] = mapped_column(
        db_enum(ContainerStatus, "container_status"), index=True
    )
    destination: Mapped[str] = mapped_column(String(100))
    weight: Mapped[float] = mapped_column(Numeric(10, 2))
    priority: Mapped[Priority] = mapped_column(db_enum(Priority, "container_priority"))
    terminal: Mapped[str] = mapped_column(String(50))
    arrival_date: Mapped[date] = mapped_column(Date)

    vessel: Mapped["Vessel"] = relationship(back_populates="containers")
