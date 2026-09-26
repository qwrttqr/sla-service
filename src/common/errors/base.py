from pydantic import BaseModel


class BaseError(Exception):
    msg: str = ""

    def __init__(self, msg=None, *args, **kwargs):
        if msg:
            self.msg = msg

    def __str__(self) -> str:
        return self.msg


class BaseErrorsBatch(Exception):
    def __init__(self, errors: list[BaseError], *args, **kwargs):
        self.errors = errors
        super().__init__(*args, **kwargs)


class ErrorSchema(BaseModel):
    message: str
    reason: str
