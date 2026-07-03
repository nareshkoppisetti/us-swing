"""
File path: backend/core/exceptions.py
Purpose: Custom exception hierarchy for the USA Swing platform.
         All exceptions include a machine-readable code and HTTP status.
         Caught by the global exception handler in core/middleware.py.

SPEC Reference: Section 9.1 (Error Handling Strategy)
BUILD_PLAN Reference: Phase 1.2
"""


class AppException(Exception):
    """
    Base exception for all USA Swing application errors.
    Attributes:
        status_code: HTTP status code to return to the client
        code:        Machine-readable string code (used by frontend for i18n/handling)
        message:     Human-readable error message
        details:     Optional extra context (field errors, retry hints, etc.)
    """
    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, details: dict | None = None):
        self.message = message or self.__class__.message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ── Authentication & Authorization ────────────────────────────────────────────

class AuthenticationError(AppException):
    """Invalid/expired/missing JWT token. → HTTP 401"""
    status_code = 401
    code = "AUTHENTICATION_FAILED"
    message = "Authentication failed. Please log in again."


class AuthorizationError(AppException):
    """User lacks required role for this operation. → HTTP 403"""
    status_code = 403
    code = "AUTHORIZATION_FAILED"
    message = "You do not have permission to perform this action."


# ── Resource Errors ───────────────────────────────────────────────────────────

class NotFoundError(AppException):
    """Requested resource does not exist in the database. → HTTP 404"""
    status_code = 404
    code = "NOT_FOUND"
    message = "The requested resource was not found."


class ValidationError(AppException):
    """Request body or query params failed validation. → HTTP 422"""
    status_code = 422
    code = "VALIDATION_ERROR"
    message = "Request validation failed."


class ConflictError(AppException):
    """Resource already exists (e.g. duplicate username). → HTTP 409"""
    status_code = 409
    code = "CONFLICT"
    message = "A resource with this identifier already exists."


# ── Data / Market ─────────────────────────────────────────────────────────────

class DataUnavailableError(AppException):
    """All data source fallbacks exhausted for a symbol/data type. → HTTP 503"""
    status_code = 503
    code = "DATA_UNAVAILABLE"
    message = "Market data is temporarily unavailable. Please try again shortly."


class DataValidationError(AppException):
    """Fetched data failed OHLCV quality checks. → HTTP 422"""
    status_code = 422
    code = "DATA_VALIDATION_FAILED"
    message = "Fetched data failed quality validation."


class SymbolNotFoundError(AppException):
    """Ticker symbol does not exist in the symbol registry. → HTTP 404"""
    status_code = 404
    code = "SYMBOL_NOT_FOUND"
    message = "Symbol not found in the registry."


class RateLimitError(AppException):
    """External API daily/minute request limit reached. → HTTP 429"""
    status_code = 429
    code = "RATE_LIMIT_EXCEEDED"
    message = "Request rate limit exceeded. Please wait before retrying."


class CircuitOpenError(AppException):
    """Data source circuit breaker is open (too many failures). → HTTP 503"""
    status_code = 503
    code = "CIRCUIT_BREAKER_OPEN"
    message = "Data source is temporarily unavailable due to repeated failures."


# ── Agent Errors ──────────────────────────────────────────────────────────────

class AgentExecutionError(AppException):
    """An individual agent raised an unhandled exception. → HTTP 500"""
    status_code = 500
    code = "AGENT_EXECUTION_FAILED"
    message = "Agent execution failed."


class AgentDependencyError(AppException):
    """A required dependency agent output is missing from context. → HTTP 500"""
    status_code = 500
    code = "AGENT_DEPENDENCY_MISSING"
    message = "Required agent dependency output is missing."


# ── Prediction Errors ─────────────────────────────────────────────────────────

class PredictionNotFoundError(AppException):
    """Prediction ID does not exist in the database. → HTTP 404"""
    status_code = 404
    code = "PREDICTION_NOT_FOUND"
    message = "Prediction not found."


class PredictionGenerationError(AppException):
    """Prediction engine failed to produce an output. → HTTP 500"""
    status_code = 500
    code = "PREDICTION_GENERATION_FAILED"
    message = "Prediction generation failed."


# ── LLM / Explainability ─────────────────────────────────────────────────────

class LLMClientError(AppException):
    """Grok API call failed (network, auth, rate limit). → HTTP 502"""
    status_code = 502
    code = "LLM_CLIENT_ERROR"
    message = "LLM API call failed. Falling back to template narrative."


class ExplanationGenerationError(AppException):
    """Both LLM and fallback builder failed. → HTTP 500"""
    status_code = 500
    code = "EXPLANATION_GENERATION_FAILED"
    message = "Explanation generation failed."
