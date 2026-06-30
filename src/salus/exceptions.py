class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found") -> None:
        self.message = message
        super().__init__(message)


class ConflictError(Exception):
    def __init__(self, message: str = "Resource already exists") -> None:
        self.message = message
        super().__init__(message)


class AuthenticationError(Exception):
    def __init__(self, message: str = "Authentication required") -> None:
        self.message = message
        super().__init__(message)


class InvalidCredentialsError(Exception):
    def __init__(self, message: str = "Invalid username or password") -> None:
        self.message = message
        super().__init__(message)


class ForbiddenError(Exception):
    def __init__(self, message: str = "Forbidden") -> None:
        self.message = message
        super().__init__(message)
