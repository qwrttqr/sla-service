from core.domain.assignment import Plan
from core.domain.engineer import Engineer
from core.domain.request import Request


class Planner:

    @staticmethod
    def build(engineers: list[Engineer], requests: list[Request]) -> Plan:
        pass