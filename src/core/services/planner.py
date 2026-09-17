from src.core.domain.assignment import Plan
from src.core.domain.engineer import Engineer
from src.core.domain.request import Request


class Planner:

    @staticmethod
    def build(engineers: list[Engineer], requests: list[Request]) -> Plan:
        pass