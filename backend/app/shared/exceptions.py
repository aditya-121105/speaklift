"""
Centralized exception hierarchy for SpeakLift.

All custom exceptions inherit from SpeakLiftException.
This allows global exception handlers to catch all domain exceptions.
"""


class SpeakLiftException(Exception):
    """Base exception for all SpeakLift domain errors."""
    status_code: int = 400
    detail: str = "An error occurred"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class ValidationError(SpeakLiftException):
    """Raised when request validation fails."""
    status_code = 400
    detail = "Validation error"


class NotFoundError(SpeakLiftException):
    """Base class for resource not found errors."""
    status_code = 404
    detail = "Resource not found"


class InterviewSessionNotFoundError(NotFoundError):
    """Raised when an interview session is not found."""
    detail = "Interview session not found"


class InterviewQuestionNotFoundError(NotFoundError):
    """Raised when an interview question is not found."""
    detail = "Interview question not found"


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found."""
    detail = "User not found"


class UnauthorizedError(SpeakLiftException):
    """Raised when user lacks required permissions."""
    status_code = 401
    detail = "Unauthorized"


class ConflictError(SpeakLiftException):
    """Raised when there's a conflict with the current state."""
    status_code = 409
    detail = "Conflict"


class UserAlreadyExistsError(ConflictError):
    """Raised when attempting to create a user with an existing email."""
    detail = "Email already registered"


class AuthenticationError(SpeakLiftException):
    """Base class for authentication errors."""
    status_code = 401
    detail = "Authentication error"


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""
    detail = "Invalid email or password"


class InvalidSessionStateError(ConflictError):
    """Raised when attempting an invalid operation on a session."""
    detail = "Invalid session state"


class EvaluationError(SpeakLiftException):
    """Raised when evaluation fails."""
    status_code = 500
    detail = "Evaluation error"