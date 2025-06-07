class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BadRequestError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)