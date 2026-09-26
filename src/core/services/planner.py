import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

import httpx

from core.domain.assignment import Assignment, Plan, UnassignedRequest
from core.domain.engineer import Engineer, VehicleType
from core.domain.office import Office
from core.domain.request import Request
from core.services.osrm_travel_time import OsrmTravelTime

Coords = tuple[float, float]

VEHICLE_PROFILE: dict[VehicleType, str] = {
    VehicleType.CAR: "driving",
    VehicleType.BICYCLE: "bicycle",
    VehicleType.WALK: "foot",
}


def haversine_km(a: Coords, b: Coords) -> float:
    lat1, lon1 = a
    lat2, lon2 = b
    r = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    h = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(h), sqrt(1 - h))


def nearest_office(point: Coords, offices: list[Office]) -> Office:
    return min(offices, key=lambda o: haversine_km(o.coords, point))


@dataclass
class EngineerState:
    engineer: Engineer
    position: Coords          # Начинаем с офиса
    free_at: datetime         # сначала освободимся в начало своей смены
    route: list[int] = field(default_factory=list)


@dataclass
class Candidate:
    state: EngineerState
    travel_min: float
    arrival: datetime
    finish: datetime


def is_eligible(e: Engineer, r: Request) -> bool:
    if r.required_vehicle_type is not None and e.vehicle_type != r.required_vehicle_type:
        return False
    if not r.required_skills <= e.skills:
        return False
    if r.required_equipment and not r.required_equipment <= e.equipment:
        return False
    return True


class Planner:
    def __init__(self, travel: dict[VehicleType, OsrmTravelTime]):
        self.travel = travel

    """
    Выбираем инженера на заявку: сначала внутри офиса (район), при неудаче — по всему городу.
    Более ранние заявки идут первыми, после по приоритету.
    """
    async def build(self, engineers: list[Engineer], offices: list[Office], requests: list[Request]) -> Plan:
        states = [EngineerState(e, e.starting_point_coords, e.shift_start) for e in engineers]
        states_by_office: dict[int, list[EngineerState]] = {}
        for s in states:
            states_by_office.setdefault(s.engineer.office_id, []).append(s)

        assignments: list[Assignment] = []
        unassigned: list[UnassignedRequest] = []

        for req in sorted(requests, key=lambda r: (r.request_start, r.priority)):
            office = nearest_office(req.point_coords, offices)
            district = [s for s in states_by_office.get(office.id, []) if is_eligible(s.engineer, req)]

            candidates = await self._evaluate(district, req)
            if not candidates:
                city = [s for s in states if is_eligible(s.engineer, req)]
                candidates = await self._evaluate(city, req)

            if not candidates:
                unassigned.append(UnassignedRequest(
                    request_id=req.id, reason="no engineer with matching vehicle/skills/equipment, or none can finish within the window/shift"))
                continue

            # Побеждает тот, кто первым эту заявку закончит
            best = min(candidates, key=lambda c: (c.travel_min, c.finish))
            best.state.route.append(req.id)
            best.state.position = req.point_coords
            best.state.free_at = best.finish
            assignments.append(Assignment(
                request_id=req.id,
                engineer_id=best.state.engineer.id,
                order=len(best.state.route),
                planned_arrival=best.arrival.time(),
                travel_minutes=round(best.travel_min),
            ))

        return Plan(assignments=assignments, unassigned=unassigned)

    """
    Выбираем самую ближайшую по затрачиваемому времени
    """
    async def _evaluate(self, states: list[EngineerState], req: Request) -> list[Candidate]:
        async def travel_min(s: EngineerState) -> float | None:
            vehicle = s.engineer.vehicle_type
            profile = VEHICLE_PROFILE.get(vehicle)
            if profile is None:
                return None  # no OSRM profile for this vehicle type yet (e.g. public transport)
            try:
                m = await self.travel[vehicle].matrix_minutes([s.position], [req.point_coords], profile)
            except httpx.HTTPError:
                return None
            return m[0][0]

        times = await asyncio.gather(*(travel_min(s) for s in states))

        out = []
        for s, t in zip(states, times):
            if t is None:  # unroutable
                continue
            arrival = s.free_at + timedelta(minutes=t)
            start = max(arrival, req.request_start)  # wait if early
            finish = start + timedelta(minutes=req.duration_minutes)
            if finish > min(req.request_end, s.engineer.shift_end):
                continue
            out.append(Candidate(s, t, arrival, finish))
        return out