from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import Container, ContainerStatus, Vessel


def count_by_status(db: Session, status: ContainerStatus) -> int:
    stmt = select(func.count()).select_from(Container).where(Container.status == status)
    return db.execute(stmt).scalar_one()


def get_by_container_number(db: Session, container_number: str) -> Container | None:
    stmt = select(Container).where(Container.container_number == container_number)
    return db.execute(stmt).scalar_one_or_none()


def get_by_vessel_name(db: Session, vessel_name: str) -> list[Container]:
    stmt = (
        select(Container)
        .join(Vessel)
        .where(Vessel.vessel_name == vessel_name)
        .order_by(Container.container_number)
    )
    return list(db.execute(stmt).scalars().all())
