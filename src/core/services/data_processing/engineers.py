import io

import pandas as pd

from core.domain.engineer import Equipment
from src.core.domain.engineer import Engineer, VehicleType, Skill


class EngineerBuilder:
    SKILL_MAP: dict[str, Skill] = {
        "skill_local_works": Skill.LOCAL,
        "skill_connection_works": Skill.CONNECTION,
        "skill_emergency_works": Skill.EMERGENCY,
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
    def __build_skill_set_from_str(skills_info: str) -> set[Equipment]:
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

    @staticmethod
    def __build_engineer_equipment_and_skills(control_df: pd.DataFrame) -> pd.DataFrame:
        _start = pd.to_datetime(control_df["Начало"], format="%d.%m.%Y %H:%M")
        _end = pd.to_datetime(control_df["Окончание"], format="%d.%m.%Y %H:%M")

        agg_kwargs = {
            "shift_start": ("_start", "min"),
            "shift_end": ("_end", "max"),
            "gigabit_connection": ("Гигабитное подключение", lambda s: "Да" in set(s.dropna().unique())),
        }

        if "Подключение" in control_df.columns:
            agg_kwargs["equipment_types"] = (
                "Подключение",
                lambda s: set(s.dropna().unique())
            )

        engineers_df = (
            control_df.assign(_start=_start, _end=_end)
            .dropna(subset=["Бригада"])
            .groupby("Бригада")
            .agg(**agg_kwargs)
            .reset_index()
            .sort_values("shift_start")
        )

        engineers_df["shift_start"] = engineers_df["shift_start"].dt.time
        engineers_df["shift_end"] = engineers_df["shift_end"].dt.time

        if "equipment_types" not in engineers_df.columns:
            engineers_df["equipment_types"] = [set() for _ in range(len(engineers_df))]

        def _build_equipment(row):
            equipment = set(row["equipment_types"]) if row["equipment_types"] else set()
            if row["gigabit_connection"]:
                equipment.add("gigabit_connection")
            return equipment or None

        engineers_df["equipment"] = engineers_df.apply(_build_equipment, axis=1)
        engineers_df = engineers_df.drop(columns=["equipment_types", "gigabit_connection"])
        skill_cols = ["skill_local_works", "skill_connection_works", "skill_emergency_works"]

        skill_by_brigade = (
            engineers_df.dropna(subset=["Бригада"])
            .groupby("Бригада")[skill_cols]
            .any()
        )

        engineers_df = engineers_df.merge(skill_by_brigade, left_on="Бригада", right_index=True, how="left")
        for col in skill_cols:
            engineers_df[col] = engineers_df[col].fillna(False)

        return engineers_df

    @staticmethod
    def build_from_scratch_csv(source: str | io.BytesIO, encoding: str = "utf-8") -> list[Engineer]:
        engineers = []

        df = pd.read_csv(source, encoding=encoding)

        engineers_df = EngineerBuilder.__build_engineer_equipment_and_skills(df)
        for i, row in enumerate(engineers_df.itertuples()):
            engineers.append(
                Engineer(
                    id=i,
                    starting_point_coords=row.start_point_coords,
                    shift_start=row.shift_start,
                    shift_end=row.shift_end,
                    skills=EngineerBuilder.__build_skill_set_from_str(row.skills),
                    equipment=EngineerBuilder.__build_equipment_set_from_str(row.equipment),  # or derived from can_gigabit/equipment_types
                    vehicle_type=row.vehicle_type,
                )
            )

        return engineers
