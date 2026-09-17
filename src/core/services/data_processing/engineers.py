import pandas as pd

from src.core.domain.engineer import Engineer, VehicleType, Skill


def get_engineers_info(control_df: pd.DataFrame) -> pd.DataFrame:
    _start = pd.to_datetime(control_df["Начало"], format="%d.%m.%Y %H:%M")
    _end = pd.to_datetime(control_df["Окончание"], format="%d.%m.%Y %H:%M")

    agg_kwargs = {
        "shift_start": ("_start", "min"),
        "shift_end": ("_end", "max"),
        "can_gigabit": ("Гигабитное подключение", lambda s: "Да" in set(s.dropna().unique())),
    }

    if "Подключение" in control_df.columns:
        agg_kwargs["equipment_types"] = (
            "Подключение",
            lambda s: set(s.dropna().unique()) or None
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
        engineers_df["equipment_types"] = [None for _ in range(len(engineers_df))]

    return engineers_df

VEHICLE_TYPE_MAP: dict[str, VehicleType] = {
    "Автомобиль": VehicleType.CAR,
    "Пешеход": VehicleType.WALK,
    "Велосипед": VehicleType.BICYCLE,
    "Общественный транспорт": VehicleType.PUBLIC_TRANSPORT,
}

SKILL_MAP: dict[str, Skill] = {
    "Локальные работы": Skill.LOCAL,
    "Работы на подключение и дозаказы": Skill.CONNECTION,
    "Аварийные работы": Skill.EMERGENCY,
}

def parse_vehicle_type(raw: str) -> VehicleType:
    try:
        return VEHICLE_TYPE_MAP[raw.strip()]
    except KeyError:
        raise ValueError(f"Unknown vehicle type: {raw!r}")

def build_engineers(engineers_df: pd.DataFrame) -> list[Engineer]:
    engineers = []
    for i, row in enumerate(engineers_df.itertuples()):
        engineers.append(
            Engineer(
                id=i,
                current_point_coords = row.start_point_coords,
                shift_start=row.shift_start,
                shift_end=row.shift_end,
                skills=row.skills,          # or derived from can_gigabit/equipment_types
                vehicle_type=row.vehicle_type ,
            )
        )
    return engineers