from core.services.geocoder import GeocoderService
from src.core.domain.assignment import Plan
from src.core.domain.engineer import Engineer
from src.core.domain.request import Request


class Planner:
    def __init__(self, geocoder: GeocoderService):
        self.geocoder = geocoder

    @staticmethod
    def build(engineers: list[Engineer], requests: list[Request]) -> Plan:
        print(engineers)
        print(requests)