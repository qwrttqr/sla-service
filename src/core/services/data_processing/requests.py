import ast
import asyncio
import io
from datetime import datetime

import pandas as pd

from common.types import WorkType, Status
from core.services.geocoder import GeocoderService
from core.services.local_cache import get_from_cache, save_to_cache
from common.types import Skill, VehicleType, Equipment
from core.entities import Request


class RequestBuilder:
    SKILL_MAP: dict[str, Skill] = {
        "skill_local_works": Skill.LOCAL_WORKS,
        "skill_connection_works": Skill.CONNECTION_WORKS,
        "skill_emergency_works": Skill.EMERGENCY_WORKS,
    }

    EQUIPMENT_MAP: dict[str, Equipment] = {
        "FMC": Equipment.FMC,
        "FTTB": Equipment.FTTB,
        "gigabit_connection": Equipment.gigabit_connection,
    }

    VEHICLE_TYPE_MAP: dict[str, VehicleType] = {
        "car": VehicleType.CAR,
        "walk": VehicleType.WALK,
        "bicycle": VehicleType.BICYCLE,
        "public_transport": VehicleType.PUBLIC_TRANSPORT,
    }

    WORK_TYPE_MAP: dict[str, WorkType] = {
        "connect_client": WorkType.CONNECT_CLIENT,
        "emergency_work": WorkType.EMERGENCY_WORK,
        "local_work_or_repair": WorkType.LOCAL_WORK_OR_REPAIR,
        "postorder": WorkType.POST_ORDER,
    }

    STATUS_MAP: dict[str, Status] = {
        "sent": Status.SENT,
        "cancelled": Status.CANCELLED,
        "on_the_way": Status.ON_THE_WAY,
        "done": Status.DONE,
    }

    DATETIME_FMT = "%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, geocoder: GeocoderService):
        self.geocoder_service = geocoder

    @staticmethod
    def __parse_set(raw) -> set[str]:
        """CSV cell like "{'FMC', 'FTTB'}" -> {'FMC', 'FTTB'}; empty/NaN -> set()."""
        if not isinstance(raw, str) or not raw.strip():
            return set()
        return {str(item).strip() for item in ast.literal_eval(raw)}

    @staticmethod
    def __build_equipment_set_from_str(equipment_info) -> set[Equipment] | None:
        mapped_equipment = set()
        for item in RequestBuilder.__parse_set(equipment_info):
            try:
                mapped_equipment.add(RequestBuilder.EQUIPMENT_MAP[item])
            except KeyError:
                raise ValueError(f"Unknown equipment: {item!r}")
        return mapped_equipment or None

    @staticmethod
    def __build_skill_set_from_str(skills_info) -> set[Skill]:
        mapped_skills = set()
        for item in RequestBuilder.__parse_set(skills_info):
            try:
                mapped_skills.add(RequestBuilder.SKILL_MAP[item])
            except KeyError:
                raise ValueError(f"Unknown skill: {item!r}")
        return mapped_skills

    @staticmethod
    def __build_vehicle_type_from_str(raw) -> VehicleType | None:
        if not isinstance(raw, str) or not raw.strip():
            return None  # walk = no requirement
        try:
            return RequestBuilder.VEHICLE_TYPE_MAP[raw.strip()]
        except KeyError:
            raise ValueError(f"Unknown vehicle type: {raw!r}")

    @staticmethod
    def __build_work_type_from_str(raw) -> WorkType:
        try:
            return RequestBuilder.WORK_TYPE_MAP[raw.strip()]
        except KeyError:
            raise ValueError(f"Unknown work type type: {raw!r}")

    @staticmethod
    def __build_status_from_str(raw) -> Status:
        try:
            return RequestBuilder.STATUS_MAP[raw.strip()]
        except KeyError:
            raise ValueError(f"Unknown work type type: {raw!r}")

    async def build_from_csv(self, source: str | io.BytesIO, encoding: str = "utf-8") -> list[Request]:
        df = pd.read_csv(source, encoding=encoding, header=0)

        coords_by_address: dict[str, tuple[float, float]] = {}
        active_network_tasks: dict[str, asyncio.Task] = {}
        for row in df.itertuples():
            address = str(row.address).lower()
            if address in coords_by_address or address in active_network_tasks:
                continue

            cached_coords = get_from_cache(address)
            if cached_coords is not None:
                coords_by_address[address] = cached_coords
            else:
                active_network_tasks[address] = asyncio.create_task(self.geocoder_service.get_coordinates(address))

        if active_network_tasks:
            await asyncio.gather(*active_network_tasks.values())

        for address, task in active_network_tasks.items():
            coords = task.result()
            save_to_cache(address, coords)
            coords_by_address[address] = coords

        requests = []
        for row in df.itertuples():
            address = str(row.address).lower()
            requests.append(
                Request(
                    id=int(row.request_id),
                    point_coords=coords_by_address[address],
                    status=self.__build_status_from_str(row.status),
                    work_type=self.__build_work_type_from_str(row.work_type),
                    request_start=datetime.strptime(row.window_start, self.DATETIME_FMT),
                    request_end=datetime.strptime(row.window_end, self.DATETIME_FMT),
                    required_skills=RequestBuilder.__build_skill_set_from_str(row.required_skills),
                    required_vehicle_type=RequestBuilder.__build_vehicle_type_from_str(row.required_vehicle),
                    required_equipment=RequestBuilder.__build_equipment_set_from_str(row.required_equipment),
                )
            )

        return requests
