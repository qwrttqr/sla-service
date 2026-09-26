from datetime import time

# --- Офис (один на всех, как в исходнике) ---
OFFICE = "г. Москва, ул Юных Ленинцев, д 83 к4"

# --- Дата смен ---
BASE_DATE = "2026-08-17"

# --- Смены ---
SHIFT_OPTIONS = [
    (time(10, 0), time(16, 0)),
    (time(10, 0), time(18, 0)),
    (time(10, 0), time(20, 0)),
    (time(10, 0), time(22, 0)),
]

# --- Временные окна ---
WINDOW_SLOTS = [
    (time(10, 0), time(12, 0)),
    (time(12, 0), time(14, 0)),
    (time(14, 0), time(16, 0)),
    (time(16, 0), time(18, 0)),
    (time(18, 0), time(20, 0)),
    (time(20, 0), time(22, 0)),
]

# --- Справочники (как строки, чтобы совпадать с CSV) ---
ALL_SKILLS = [
    "skill_local_works",
    "skill_connection_works",
    "skill_emergency_works",
]

ALL_VEHICLES = ["car", "walk", "bicycle"] # убрал паблик транспорт

ALL_EQUIPMENT = ["FMC", "FTTB", "gigabit_connection"]

ALL_WORK_TYPES = [
    "connect_client",
    "emergency_work",
    "local_work_or_repair",
    "postorder",
]

ALL_STATUSES = ["sent", "on_the_way", "done", "cancelled"]

# --- Веса ---
WORK_TYPE_WEIGHTS = {
    "connect_client": 0.30,
    "emergency_work": 0.20,
    "local_work_or_repair": 0.30,
    "postorder": 0.20,
}

STATUS_WEIGHTS = {
    "sent": 0.50,
    "on_the_way": 0.20,
    "done": 0.20,
    "cancelled": 0.10,
}

# --- Распределение навыков у инженеров ---
# 30% — 3 навыка, 50% — 2 навыка, 20% — 1 навык
ENGINEER_SKILL_DISTRIBUTION = [(3, 0.30), (2, 0.50), (1, 0.20)]

# --- Соответствие work_type → required_skill ---
WORK_TYPE_SKILL_MAP = {
    "connect_client": "skill_connection_works",
    "emergency_work": "skill_emergency_works",
    "local_work_or_repair": "skill_local_works",
    "postorder": "skill_local_works",
}