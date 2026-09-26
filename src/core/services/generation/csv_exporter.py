import csv
import io


ENGINEER_FIELDS = [
    "name", "shift_start", "shift_end",
    "equipment", "skills", "vehicle", "office",
]

REQUEST_FIELDS = [
    "request_id", "address", "work_type",
    "window_start", "window_end",
    "required_skills", "required_vehicle",
    "status", "required_equipment",
]


def rows_to_csv(rows: list[dict], fieldnames: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fieldnames,
        quoting=csv.QUOTE_MINIMAL,   # кавычки только там, где нужно
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def engineers_to_csv(rows: list[dict]) -> str:
    return rows_to_csv(rows, ENGINEER_FIELDS)


def requests_to_csv(rows: list[dict]) -> str:
    return rows_to_csv(rows, REQUEST_FIELDS)