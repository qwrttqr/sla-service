from common.errors.base import BaseError
from common.errors.errors import BaseNotFoundError


class TravelTimeUnavailable(BaseNotFoundError):
    msg = "Не удалось получить матрицу времени в пути"

class TravelTimeUnsupportedTransportType(BaseError):
    msg = "Данный тип транспорта не поддерживается"