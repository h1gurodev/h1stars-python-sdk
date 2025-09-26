"""
H1Stars SDK Exceptions
"""


class H1StarsError(Exception):
    """Base exception for all H1Stars SDK errors"""
    pass


class H1StarsAPIError(H1StarsError):
    """Base API error"""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class H1StarsAuthError(H1StarsAPIError):
    """Authentication error (401)"""
    pass


class H1StarsValidationError(H1StarsAPIError):
    """Validation error (400)"""
    pass


class H1StarsNotFoundError(H1StarsAPIError):
    """Resource not found error (404)"""
    pass


class H1StarsRateLimitError(H1StarsAPIError):
    """Rate limit exceeded error (429)"""
    pass


class H1StarsServerError(H1StarsAPIError):
    """Server error (500)"""
    pass