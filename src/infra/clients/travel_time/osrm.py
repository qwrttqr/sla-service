import httpx

from core.clients.travel_time.base_client import BaseTravelTimeClient
from core.clients.travel_time.exceptions import TravelTimeUnavailable
from core.clients.travel_time.schemas import TravelTimeRequest, TravelTimeResponse


class OsrmTravelTimeClient(BaseTravelTimeClient):
    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None):
        self.base_url = base_url
        self.client = client or httpx.AsyncClient(timeout=10)

    async def matrix_minutes(
        self, req: TravelTimeRequest
    ) -> TravelTimeResponse | TravelTimeUnavailable:
        pts = [*req.origins, *req.destinations]
        coords = ";".join(f"{lon},{lat}" for lat, lon in pts)
        src = ";".join(map(str, range(len(req.origins))))
        dst = ";".join(
            str(len(req.origins) + i) for i in range(len(req.destinations))
        )

        try:
            r = await self.client.get(
                f"{self.base_url}/table/v1/{req.profile}/{coords}",
                params={
                    "sources": src,
                    "destinations": dst,
                    "annotations": "duration",
                },
            )
            r.raise_for_status()
        except httpx.HTTPError:
            return TravelTimeUnavailable()

        durations = r.json()["durations"]
        minutes = [
            [s / 60 if s is not None else None for s in row] for row in durations
        ]
        return TravelTimeResponse(durations_minutes=minutes)

    async def aclose(self) -> None:
        await self.client.aclose()