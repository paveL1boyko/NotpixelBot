class TapsError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class InvalidSession(BaseException): ...
