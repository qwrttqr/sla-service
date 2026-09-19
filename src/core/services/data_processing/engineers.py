import asyncio
import io
import pandas as pd

from datetime import datetime
from core.domain.engineer import Equipment
from core.services.geocoder import GeocoderService
from core.services.local_cache import get_from_cache, save_to_cache
from src.core.domain.engineer import Engineer, VehicleType, Skill


class EngineerBuilder:
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

    DATETIME_FMT = "%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, geocoder: GeocoderService):
        self.geocoder_service = geocoder

    @staticmethod
    def __build_equipment_set_from_str(equipment_info: str) -> set[Equipment]:
        equipment = set(equipment_info)
        mapped_equipment = set()
        for item in equipment:
            try:
                mapped_equipment.add(EngineerBuilder.EQUIPMENT_MAP[item.strip()])
            except KeyError:
                raise ValueError(f"Unknown vehicle type: {item!r}")
        return mapped_equipment

    @staticmethod
    def __build_skill_set_from_str(skills_info: str) -> set[Skill]:
        equipment = set(skills_info)
        mapped_skills = set()
        for item in equipment:
            try:
                mapped_skills.add(EngineerBuilder.SKILL_MAP[item.strip()])
            except KeyError:
                raise ValueError(f"Unknown skill: {item!r}")
        return mapped_skills

    @staticmethod
    def __build_vehicle_type_from_str(raw: str) -> VehicleType:
        try:
            return EngineerBuilder.VEHICLE_TYPE_MAP[raw.strip()]
        except KeyError:
            raise ValueError(f"Unknown vehicle type: {raw!r}")

    async def build_from_csv(self, source: str | io.BytesIO, encoding: str = "utf-8") -> list[Engineer]:

        df = pd.read_csv(source, encoding=encoding)

        coords_by_address: dict[str, tuple[float, float]] = {}
        active_network_tasks: dict[str, asyncio.Task] = {}
        for row in df.itertuples():
            address = str(row.address)
            if address in coords_by_address or address in active_network_tasks:
                continue
            cached_coords = get_from_cache(address)
            if cached_coords is not None:
                coords_by_address[address] = cached_coords
            else:
                active_network_tasks[address] = asyncio.create_task(self.geocoder_service.geocode(address))

        if active_network_tasks:
            await asyncio.gather(*active_network_tasks.values())

        for address, task in active_network_tasks.items():
            coords = task.result()
            save_to_cache(address, coords)
            coords_by_address[address] = coords

        engineers = []

        for i, row in enumerate(df.itertuples()):
            engineers.append(
                Engineer(
                    id=i,
                    starting_point_coords=coords_by_address[str(row.address)],
                    shift_start=datetime.strptime(row.shift_start, self.DATETIME_FMT),
                    shift_end=datetime.strptime(row.shift_end, self.DATETIME_FMT),
                    skills=EngineerBuilder.__build_skill_set_from_str(row.skills),
                    equipment=EngineerBuilder.__build_equipment_set_from_str(row.equipment),
                    vehicle_type=EngineerBuilder.__build_vehicle_type_from_str(row.vehicle_type),
                )
            )

        return engineers
