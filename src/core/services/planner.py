import asyncio
import math
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import atan2, cos, radians, sin, sqrt

import httpx

from common.types import GeoPoint, VehicleType
from core.clients.travel_time.exceptions import TravelTimeUnavailable, TravelTimeUnsupportedTransportType
from core.entities import (Assignment, Engineer, Office, Plan, Request,
                           UnassignedRequest)
from core.services.travel_time import TravelTimeService
logger = logging.getLogger(__name__)
TRAFFIC_JAM_COEFFICIENTS: dict[int, float] = {
    7: 1.3, 8: 1.6, 9: 1.7, 10: 1.3,
    11: 1.1, 12: 1.1, 13: 1.1, 14: 1.1, 15: 1.2,
    16: 1.3, 17: 1.6, 18: 1.8, 19: 1.7, 20: 1.4,
    21: 1.2, 22: 1.0, 23: 1.0,
}
DEFAULT_JAM_COEFFICIENT = 1.0
VEHICLES_AFFECTED_BY_TRAFFIC = {VehicleType.CAR}

@dataclass
class Slot:
    request: Request
    arrival: datetime      # earliest moment the engineer could be on site
    start: datetime        # planned start
    finish: datetime
    travel_min: float      # travel from the previous point


@dataclass
class EngineerState:
    engineer: Engineer
    slots: list[Slot] = field(default_factory=list)  # kept sorted by start


@dataclass
class Candidate:
    state: EngineerState
    index: int                         # insertion position in state.slots
    slot: Slot
    travel_to_next_slot: int | None       # travel to the following slot, if any
    next_slot_arrival: datetime | None      # new arrival time of the following slot
    added_travel_min: int


class PlannerService:
    def __init__(self, travel_time_service: TravelTimeService):
        self._travel_time_service = travel_time_service
        self._raw_travel_cache: dict[tuple, float | None] = {}
        self._sem = asyncio.Semaphore(10)

    async def build(
            self, engineers: list[Engineer], offices: list[Office], requests: list[Request]
    ) -> Plan:
        """
        Requests are placed as late as possible (minus a spare buffer) and inserted
        into gaps between the engineer's already planned slots.
        Office engineers first, whole city as a fallback.
        """
        self._raw_travel_cache = {}
        states = [EngineerState(e) for e in engineers]
        states_by_office: dict[int, list[EngineerState]] = {}
        for s in states:
            states_by_office.setdefault(s.engineer.office_id, []).append(s)

        unassigned: list[UnassignedRequest] = []

        for req in sorted(requests, key=lambda r: (r.priority, r.request_start)):
            if req.required_vehicle_type is not None:
                try:
                    self._travel_time_service.assert_transport_type_supported(
                        req.required_vehicle_type.value
                    )
                except TravelTimeUnsupportedTransportType as e:
                    unassigned.append(UnassignedRequest(request=req, reason=str(e)))
                    continue

            office = self._get_nearest_office(req.point_coords, offices)
            office_states = [
                s for s in states_by_office.get(office.id, [])
                if self._is_eligible(s.engineer, req)
            ]
            candidates = await self._evaluate(office_states, req)

            if not candidates:
                city_states = [s for s in states if self._is_eligible(s.engineer, req)]
                candidates = await self._evaluate(city_states, req)

            if not candidates:
                unassigned.append(
                    UnassignedRequest(
                        request=req,
                        reason="Под данную заявку не нашлось инженера по требованиям",
                    )
                )
                continue

            best = min(candidates, key=lambda c: (c.added_travel_min, c.slot.start))
            self._commit(best)

        return Plan(assignments=self._collect_assignments(states), unassigned=unassigned)

    async def _evaluate(self, states: list[EngineerState], req: Request) -> list[Candidate]:
        found = await asyncio.gather(*(self._find_insertion(s, req) for s in states))
        return [c for c in found if c is not None]

    async def _find_insertion(self, state: EngineerState, new_req: Request) -> Candidate | None:
        """Try every gap of the engineer's day (before the first slot, between slots,
        after the last) and return the cheapest feasible insertion."""
        engineer = state.engineer
        vehicle = engineer.vehicle_type
        duration = timedelta(minutes=new_req.duration_minutes)
        best: Candidate | None = None

        for index in range(len(state.slots) + 1):
            # Where the engineer comes from and when he is free to leave
            if index == 0:
                prev_pos, prev_free_at = engineer.starting_point_coords, engineer.shift_start
            else:
                prev_slot = state.slots[index - 1]
                prev_pos, prev_free_at = prev_slot.request.point_coords, prev_slot.finish
            next_slot = state.slots[index] if index < len(state.slots) else None

            # Getting to the new request
            travel_to_new = await self._get_travel_min(
                prev_pos, new_req.point_coords, vehicle, prev_free_at
            )
            if travel_to_new is None:
                continue
            arrive_at_new = prev_free_at + timedelta(minutes=travel_to_new)
            earliest_start = max(arrive_at_new, new_req.request_start)

            # Latest start allowed by the request deadline and the end of the shift
            latest_start = min(
                new_req.arrive_before_to_accomplish,
                engineer.shift_end - duration
            )

            # The next slot is fixed, so we must finish and drive there in time
            if next_slot is not None:
                travel_to_next_estimate = await self._get_travel_min(
                    new_req.point_coords, next_slot.request.point_coords, vehicle, next_slot.start
                )
                if travel_to_next_estimate is None:
                    continue
                latest_start = min(
                    latest_start,
                    next_slot.start - timedelta(minutes=travel_to_next_estimate) - duration,
                )

            if earliest_start > latest_start:
                continue  # the gap is too small

            # As late as possible, to leave the most free time before this job.
            # Use `start = earliest_start` for the classic "as early as possible".
            start = latest_start
            finish = start + duration

            # Exact check: traffic depends on the real departure time (finish)
            travel_to_next = None
            arrive_at_next = None
            if next_slot is not None:
                travel_to_next = await self._get_travel_min(
                    new_req.point_coords, next_slot.request.point_coords, vehicle, finish
                )
                if travel_to_next is None:
                    continue
                arrive_at_next = finish + timedelta(minutes=travel_to_next)
                if arrive_at_next > next_slot.start:
                    continue

            candidate = Candidate(
                state=state,
                index=index,
                slot=Slot(new_req, arrive_at_new, start, finish, travel_to_new),
                travel_to_next_slot=travel_to_next,
                next_slot_arrival=arrive_at_next,
                added_travel_min=travel_to_new + (travel_to_next or 0),
            )
            if best is None or (candidate.added_travel_min, candidate.slot.start) < (
                    best.added_travel_min, best.slot.start):
                best = candidate

        return best

    @staticmethod
    def _commit(c: Candidate) -> None:
        slots = c.state.slots
        slots.insert(c.index, c.slot)
        if c.index + 1 < len(slots):
            if c.next_slot_arrival and c.travel_to_next_slot:
                nxt = slots[c.index + 1]
                nxt.arrival = c.next_slot_arrival
                nxt.travel_min = c.travel_to_next_slot

    @staticmethod
    def _collect_assignments(states: list[EngineerState]) -> list[Assignment]:
        out = []
        for s in states:
            for order, slot in enumerate(s.slots, start=1):
                out.append(
                    Assignment(
                        request_id=slot.request.id,
                        engineer_id=s.engineer.id,
                        order=order,
                        planned_arrival=slot.arrival,
                        planned_start=slot.start,
                        planned_finish=slot.finish,
                        wait_minutes=round((slot.start - slot.arrival).total_seconds() / 60),
                        travel_minutes=round(slot.travel_min),
                    )
                )
        return out

    async def _get_travel_min(
            self, a: GeoPoint, b: GeoPoint, vehicle: VehicleType, depart: datetime
    ) -> int | None:
        key = (a.lat, a.lon, b.lat, b.lon, vehicle)
        if key not in self._raw_travel_cache:
            try:
                async with self._sem:
                    m = await self._travel_time_service.get_matrix([a], [b], vehicle)
                self._raw_travel_cache[key] = m[0][0]
            except TravelTimeUnsupportedTransportType:
                self._raw_travel_cache[key] = None   # permanent, safe to cache
            except (httpx.HTTPError, TravelTimeUnavailable) as e:
                logger.warning("travel time failed %s -> %s: %r", a, b, e)
                return None                           # transient: don't cache
        raw = self._raw_travel_cache[key]
        if raw is None:
            return None
        return math.ceil(raw * self._get_jam_coefficient(depart, vehicle))

    def _get_nearest_office(self, point: GeoPoint, offices: list[Office]) -> Office:
        return min(offices, key=lambda o: self._haversine_km(o.coords, point))

    @staticmethod
    def _haversine_km(a: GeoPoint, b: GeoPoint) -> float:
        lat1, lon1 = a.lat, a.lon
        lat2, lon2 = b.lat, b.lon
        r = 6371.0
        dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
        h = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        return 2 * r * atan2(sqrt(h), sqrt(1 - h))

    @staticmethod
    def _is_eligible(e: Engineer, r: Request) -> bool:
        if r.district not in e.districts:
            return False
        if r.required_vehicle_type is not None and e.vehicle_type != r.required_vehicle_type:
            return False
        if not r.required_skills <= e.skills:
            return False
        if r.required_equipment and not r.required_equipment <= e.equipment:
            return False
        return True

    @staticmethod
    def _get_jam_coefficient(at: datetime, vehicle_type: VehicleType) -> float:
        """
        `at` is expected to be timezone-aware UTC (the whole pipeline works in UTC).
        Traffic coefficients are keyed by Moscow local hour, so we convert UTC -> MSK.
        """
        MSK = timezone(timedelta(hours=3))
        if vehicle_type not in VEHICLES_AFFECTED_BY_TRAFFIC:
            return 1.0

        # To UTC
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        # To MSC
        msk_hour = at.astimezone(MSK).hour
        return TRAFFIC_JAM_COEFFICIENTS.get(msk_hour, DEFAULT_JAM_COEFFICIENT)