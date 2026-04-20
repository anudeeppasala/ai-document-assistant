class AppError(Exception):
    """Base application error with HTTP semantics."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BadRequestError(AppError):
    status_code = 400
    code = "bad_request"


class DependencyUnavailableError(AppError):
    status_code = 503
    code = "dependency_unavailable"


class IndexingError(AppError):
    status_code = 500
    code = "indexing_error"


class QueryError(AppError):
    status_code = 503
    code = "query_error"
