import random
from datetime import datetime, time, timedelta, timezone

from core.services.generation.address_repository import load_addresses
from core.services.generation import dictionaries as d

MSK = timezone(timedelta(hours=3))


def _combine(t: time) -> str:
    """Собирает '2026-08-17T10:00:00+0300' из даты и времени."""
    base = datetime.fromisoformat(d.BASE_DATE)
    dt = datetime.combine(base.date(), t).replace(tzinfo=MSK)
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def _set_repr(s: set) -> str:
    """Пустое множество → '', непустое → repr как в Python."""
    return str(s) if s else ""


# ---------- ИНЖЕНЕРЫ ----------
def generate_engineer_rows(n: int = 12) -> list[dict]:
    rows = []

    # распределяем транспорт равномерно
    vehicle_pool = (d.ALL_VEHICLES * (n // len(d.ALL_VEHICLES) + 1))[:n]
    random.shuffle(vehicle_pool)

    skill_counts = [c for c, _ in d.ENGINEER_SKILL_DISTRIBUTION]
    skill_weights = [w for _, w in d.ENGINEER_SKILL_DISTRIBUTION]

    for i in range(n):
        # навыки
        count = random.choices(skill_counts, weights=skill_weights)[0]
        skills = set(random.sample(d.ALL_SKILLS, count))

        # смена
        shift_start_t, shift_end_t = random.choice(d.SHIFT_OPTIONS)

        # оборудование: 0..3 элемента
        equip_n = random.randint(0, len(d.ALL_EQUIPMENT))
        equipment = set(random.sample(d.ALL_EQUIPMENT, equip_n))

        rows.append({
            "name": f"Бригада {i + 1:02d}",
            "shift_start": _combine(shift_start_t),
            "shift_end": _combine(shift_end_t),
            "equipment": _set_repr(equipment),
            "skills": _set_repr(skills),
            "vehicle": vehicle_pool[i],
            "office": d.OFFICE,
        })
    return rows


# ---------- ЗАЯВКИ ----------
def generate_request_rows(n: int = 80) -> list[dict]:
    all_addresses = load_addresses()
    if n > len(all_addresses):
        raise ValueError(
            f"Запрошено {n} заявок, но в датасете только {len(all_addresses)} адресов"
        )

    chosen_addresses = random.sample(all_addresses, n)

    rows = []

    work_types = list(d.WORK_TYPE_WEIGHTS.keys())
    work_weights = list(d.WORK_TYPE_WEIGHTS.values())
    statuses = list(d.STATUS_WEIGHTS.keys())
    status_weights = list(d.STATUS_WEIGHTS.values())

    for i, address in enumerate(chosen_addresses):
        work_type = random.choices(work_types, weights=work_weights)[0]
        status = random.choices(statuses, weights=status_weights)[0]
        win_start_t, win_end_t = random.choice(d.WINDOW_SLOTS)

        required_vehicle = (
            "" if random.random() < 0.30 else random.choice(d.ALL_VEHICLES)
        )

        if random.random() < 0.40:
            required_equipment = ""
        else:
            k = random.randint(1, 2)
            required_equipment = _set_repr(set(random.sample(d.ALL_EQUIPMENT, k)))

        required_skill = d.WORK_TYPE_SKILL_MAP[work_type]

        rows.append({
            "request_id": 100 + i,
            "address": address,
            "work_type": work_type,
            "window_start": _combine(win_start_t),
            "window_end": _combine(win_end_t),
            "required_skills": _set_repr({required_skill}),
            "required_vehicle": required_vehicle,
            "status": status,
            "required_equipment": required_equipment,
        })
    return rows