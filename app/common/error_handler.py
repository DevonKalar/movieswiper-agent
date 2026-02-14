from flask import jsonify, g, Response, Flask

# Base error classes
class AppError(Exception):
  """Base application error class."""
  def __init__(self, message: str, status_code: int = 500, error_code: str = 'INTERNAL_ERROR'):
    self.message = message
    self.status_code = status_code
    self.error_code = error_code

class NotFoundError(AppError):
  """Resource not found."""
  def __init__(self, message: str = 'Resource not found', status_code: int = 404, error_code: str = 'NOT_FOUND'):
    super().__init__(message, status_code, error_code)

class ValidationError(AppError):
  """Validation error."""
  def __init__(self, message: str = 'Validation error', status_code: int = 400, error_code: str = 'VALIDATION_ERROR'):
    super().__init__(message, status_code, error_code)

class ConflictError(AppError):
  """Conflict error."""
  def __init__(self, message: str = 'Conflict error', status_code: int = 409, error_code: str = 'CONFLICT_ERROR'):
    super().__init__(message, status_code, error_code)

class UnauthorizedError(AppError):
  """Unauthorized error."""
  def __init__(self, message: str = 'Unauthorized error', status_code: int = 401, error_code: str = 'UNAUTHORIZED_ERROR'):
    super().__init__(message, status_code, error_code)

# Error handler functions
def handle_app_error(error: AppError) -> tuple[Response, int]:
  return jsonify({
    "message": error.message,
    "error_code": error.error_code,
  }), error.status_code

def handle_uncaught_error(error: Exception) -> tuple[Response, int]:
  return jsonify({
    "message": "An unexpected error occurred",
    "error_code": "INTERNAL_ERROR",
  }), 500

# Register error handlers
def register_error_handlers(app: Flask):
  app.register_error_handler(AppError, handle_app_error)
  app.register_error_handler(Exception, handle_uncaught_error)