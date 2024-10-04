from .schemas import *


class BaseException(Exception):
    def __init__(self, message, status_code, type, schema=BaseExceptionSchema):
        self.message = message
        self.status_code = status_code
        self.type = type
        self.schema = schema

    def to_dict(self):
        return {
            "message": self.message,
            "status_code": self.status_code,
            "type": self.type,
        }

    @classmethod
    def response(cls):
        obj = cls("")
        return {obj.status_code: {"description": obj.message, "model": obj.schema}}

    def __call__(self):
        return {self.status_code: {"description": self.message, "model": self.schema}}


class BadRequestException(BaseException):
    def __init__(self, message="Bad request"):
        super().__init__(message, 400, "BadRequest", BadRequestExceptionSchema)


class UnauthorizedException(BaseException):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, 401, "Unauthorized", UnauthorizedExceptionSchema)


class NotFoundException(BaseException):
    def __init__(self, message="Not found"):
        super().__init__(message, 404, "NotFound", NotFoundExceptionSchema)


class RequestTimeoutException(BaseException):
    def __init__(self, message="Request timeout"):
        super().__init__(message, 408, "RequestTimeout", RequestTimeoutExceptionSchema)


class InternalServerErrorException(BaseException):
    def __init__(self, message="Internal server error"):
        super().__init__(
            message, 500, "InternalServerError", InternalServerErrorExceptionSchema
        )


class ServiceUnavailableException(BaseException):
    def __init__(self, message="Service unavailable"):
        super().__init__(
            message, 503, "ServiceUnavailable", ServiceUnavailableExceptionSchema
        )
