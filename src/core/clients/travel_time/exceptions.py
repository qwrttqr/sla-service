from common.errors.errors import BaseNotFoundError


class TravelTimeUnavailable(BaseNotFoundError):
    msg = "Не удалось получить матрицу времени в пути"