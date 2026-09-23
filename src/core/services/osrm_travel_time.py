import json
from datetime import datetime
from pathlib import Path
from typing import Protocol

import httpx

from core.services.travel_time_interface import TravelTimeInterface
from src.core.domain.engineer import VehicleType

Coords = tuple[float, float]  # (lat, lon)

# todo: replace with real data
_DEFAULT_WEEKDAY = [1.0] * 6 + [1.2, 1.5, 1.6, 1.4, 1.2, 1.2, 1.2, 1.2, 1.3, 1.5, 1.7, 1.8, 1.7, 1.5, 1.3, 1.2, 1.1, 1.0]
_DEFAULT_WEEKEND = [1.0] * 9 + [1.1] * 11 + [1.0] * 4


class TrafficProfile:
    def __init__(self, path: str | Path | None = None):
        if path and Path(path).exists():
            data = json.loads(Path(path).read_text())
            self.weekday, self.weekend = data["car_weekday"], data["car_weekend"]
        else:
            self.weekday, self.weekend = _DEFAULT_WEEKDAY, _DEFAULT_WEEKEND
        assert len(self.weekday) == len(self.weekend) == 24

    def factor(self, vehicle: VehicleType, t: datetime) -> float:
        if vehicle in (VehicleType.WALK, VehicleType.BICYCLE):
            return 1.0
        table = self.weekend if t.weekday() >= 5 else self.weekday
        return table[t.hour]


class OsrmTravelTime(TravelTimeInterface):
    PT_WAIT_MIN = 10  # placeholder: wait + walk to stop
    PT_CAR_RATIO = 1.6  # placeholder: PT vs free-flow car

    def __init__(
        self,
        urls: dict[VehicleType, str],
        traffic: TrafficProfile | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self.urls = urls
        self.traffic = traffic or TrafficProfile()
        self.client = client or httpx.AsyncClient(timeout=10)

    async def _table(
        self,
        base: str,
        profile: str,
        origins,
        dests
    ) -> list[list[float | None]]:
        pts = [*origins, *dests]
        coords = ";".join(f"{lon},{lat}" for lat, lon in pts)  # OSRM wants lon,lat
        src = ";".join(map(str, range(len(origins))))
        dst = ";".join(str(len(origins) + i) for i in range(len(dests)))
        r = await self.client.get(
            f"{base}/table/v1/{profile}/{coords}",
            params={"sources": src, "destinations": dst, "annotations": "duration"},
        )
        r.raise_for_status()
        return r.json()["durations"]  # seconds, None if unroutable

    async def matrix_minutes(
        self,
        origins,
        destinations,
        vehicle,
        departure
    ):
        if vehicle == VehicleType.PUBLIC_TRANSPORT:
            walk = await self._table(self.urls[VehicleType.WALK], "foot", origins, destinations)
            car = await self._table(self.urls[VehicleType.CAR], "driving", origins, destinations)
            k = self.traffic.factor(VehicleType.CAR, departure)
            out = []
            for w_row, c_row in zip(walk, car):
                row = []
                for w, c in zip(w_row, c_row):
                    pt = c / 60 * k * self.PT_CAR_RATIO + self.PT_WAIT_MIN if c is not None else None
                    cands = [x for x in (w / 60 if w is not None else None, pt) if x is not None]
                    row.append(min(cands) if cands else None)
                out.append(row)
            return out

        profile = {VehicleType.CAR: "driving", VehicleType.BICYCLE: "bicycle", VehicleType.WALK: "foot"}[vehicle]
        secs = await self._table(self.urls[vehicle], profile, origins, destinations)
        k = self.traffic.factor(vehicle, departure)
        return [[s / 60 * k if s is not None else None for s in row] for row in secs]

    async def aclose(
        self
    ) -> None:
        await self.client.aclose()
