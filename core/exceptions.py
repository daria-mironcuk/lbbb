from fastapi import HTTPException, status


class AppHTTPException(HTTPException):
    """Базовий клас для кастомних HTTP-винятків застосунку."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail: str | None = None, **kwargs):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.default_detail,
            **kwargs,
        )

    default_detail: str = "Сталася помилка"


class NotFoundError(AppHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Об'єкт не знайдено"


class BadRequestError(AppHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Некоректний запит"


class UnauthorizedError(AppHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Необхідна автентифікація"


class ForbiddenError(AppHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Доступ заборонено"


class ConflictError(AppHTTPException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Конфлікт даних"