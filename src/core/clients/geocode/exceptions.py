from common.errors.errors import BaseNotFoundError


class GeocodeNotFound(BaseNotFoundError):
    msg = "Невозможно геокодировать адрес по заданным параметрам"