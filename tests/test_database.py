from datetime import date

from app.database.models import (
    Container,
    ContainerStatus,
    ContainerType,
    Priority,
    Vessel,
    VesselStatus,
)
from app.services import container_service


def make_vessel(**overrides) -> Vessel:
    defaults = {
        "vessel_name": "MV Test Vessel",
        "voyage_number": "V2026-0001",
        "arrival_date": date(2026, 3, 1),
        "departure_date": date(2026, 3, 3),
        "status": VesselStatus.ARRIVED,
        "terminal": "Terminal A",
    }
    return Vessel(**{**defaults, **overrides})


def make_container(vessel: Vessel, **overrides) -> Container:
    defaults = {
        "container_number": "ZTCU1234567",
        "vessel": vessel,
        "container_type": ContainerType.STANDARD,
        "status": ContainerStatus.IN_YARD,
        "destination": "Rotterdam",
        "weight": 12000.5,
        "priority": Priority.NORMAL,
        "terminal": "Terminal A",
        "arrival_date": date(2026, 3, 1),
    }
    return Container(**{**defaults, **overrides})


def test_container_belongs_to_vessel(db_session):
    vessel = make_vessel()
    container = make_container(vessel)
    db_session.add(container)
    db_session.flush()

    assert container.vessel.vessel_name == "MV Test Vessel"
    assert vessel.containers == [container]


def test_count_by_status(db_session):
    vessel = make_vessel()
    db_session.add_all(
        [
            make_container(vessel, container_number="ZTCU1111111", status=ContainerStatus.DELAYED),
            make_container(vessel, container_number="ZTCU2222222", status=ContainerStatus.DELAYED),
            make_container(vessel, container_number="ZTCU3333333", status=ContainerStatus.IN_YARD),
        ]
    )
    db_session.flush()

    assert container_service.count_by_status(db_session, ContainerStatus.DELAYED) == 2
    assert container_service.count_by_status(db_session, ContainerStatus.DAMAGED) == 0


def test_get_by_container_number(db_session):
    vessel = make_vessel()
    container = make_container(vessel, container_number="ZTCU9999999")
    db_session.add(container)
    db_session.flush()

    found = container_service.get_by_container_number(db_session, "ZTCU9999999")
    assert found is not None
    assert found.container_number == "ZTCU9999999"

    assert container_service.get_by_container_number(db_session, "NOPE0000000") is None


def test_get_by_vessel_name(db_session):
    vessel = make_vessel(vessel_name="MV Northern Star")
    other_vessel = make_vessel(vessel_name="MV Pacific Horizon", voyage_number="V2026-0002")
    db_session.add_all(
        [
            make_container(vessel, container_number="ZTCU4444444"),
            make_container(other_vessel, container_number="ZTCU5555555"),
        ]
    )
    db_session.flush()

    results = container_service.get_by_vessel_name(db_session, "MV Northern Star")
    assert [c.container_number for c in results] == ["ZTCU4444444"]
