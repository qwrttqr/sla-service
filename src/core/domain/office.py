from pydantic import BaseModel


class Office(BaseModel):
    id: int
    address: str
    coords: tuple[float, float]
