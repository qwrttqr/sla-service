from functools import lru_cache
from pathlib import Path
import random

ADDRESSES_FILE = Path(__file__).resolve().parents[4] / "data" / "addresses" / "moscow_vao.csv"


@lru_cache(maxsize=1)
def load_addresses() -> tuple[str, ...]:
    """
    Читает CSV с единственной колонкой 'address' один раз и кэширует.

    Формат файла:
        address
        город Москва,Косинская улица,дом 26А
        ...

    Возвращает кортеж строк-адресов (без заголовка, без пустых строк).
    """
    if not ADDRESSES_FILE.exists():
        raise FileNotFoundError(f"Файл с адресами не найден: {ADDRESSES_FILE}")

    lines = ADDRESSES_FILE.read_text(encoding="utf-8").splitlines()

    # пропускаем первую строку (заголовок 'address')
    addresses = [
        line.strip().strip('"')
        for line in lines[1:]
        if line.strip()
    ]

    if not addresses:
        raise RuntimeError(f"Файл с адресами пуст: {ADDRESSES_FILE}")

    return tuple(addresses)


def random_address() -> str:
    return random.choice(load_addresses())