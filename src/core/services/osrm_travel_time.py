import httpx

Coords = tuple[float, float]


class OsrmTravelTime:
    """Computes travel time between coordinate pairs via an OSRM /table endpoint.
    Knows nothing about vehicles, skills, equipment, or traffic — just profile + coords."""

    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None):
        self.base_url = base_url
        self.client = client or httpx.AsyncClient(timeout=10)

    async def matrix_minutes(
        self, origins: list[Coords], destinations: list[Coords], profile: str
    ) -> list[list[float | None]]:
        pts = [*origins, *destinations]
        coords = ";".join(f"{lon},{lat}" for lat, lon in pts)
        src = ";".join(map(str, range(len(origins))))
        dst = ";".join(str(len(origins) + i) for i in range(len(destinations)))
        r = await self.client.get(
            f"{self.base_url}/table/v1/{profile}/{coords}",
            params={"sources": src, "destinations": dst, "annotations": "duration"},
        )
        r.raise_for_status()
        durations = r.json()["durations"]
        return [[s / 60 if s is not None else None for s in row] for row in durations]

    async def aclose(self) -> None:
        await self.client.aclose()