class BaseAppException(Exception):
    """Base exception for all system-related application errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class EntityNotFoundException(BaseAppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class AuthenticationException(BaseAppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class PermissionDeniedException(BaseAppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)

class DuplicateEntityException(BaseAppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)

class ValidationException(BaseAppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)

class RateLimitException(BaseAppException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)
