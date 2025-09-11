# src/exceptions.py
"""Custom exceptions for the Iris API."""


class IrisAPIException(Exception):
    """Base exception for Iris API."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(IrisAPIException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, 400)


class IrisNotFoundError(IrisAPIException):
    """Raised when an iris record is not found."""

    def __init__(self, iris_id: int):
        super().__init__(f"Iris with ID {iris_id} not found", 404)


class SpeciesNotFoundError(IrisAPIException):
    """Raised when a species is not found."""

    def __init__(self, species_name: str):
        super().__init__(f"Species '{species_name}' not found", 404)
