from pydantic import BaseModel


class BaseExceptionSchema(BaseModel):
    message: str
    status_code: int = 404
    type: str


class BadRequestExceptionSchema(BaseModel):
    message: str
    status_code: int = 400
    type: str = "BadRequest"


class UnauthorizedExceptionSchema(BaseModel):
    message: str
    status_code: int = 401
    type: str = "Unauthorized"


class NotFoundExceptionSchema(BaseModel):
    message: str
    status_code: int = 404
    type: str = "NotFound"


class RequestTimeoutExceptionSchema(BaseModel):
    message: str
    status_code: int = 408
    type: str = "RequestTimeout"


class InternalServerErrorExceptionSchema(BaseModel):
    message: str
    status_code: int = 500
    type: str = "InternalServerError"


class ServiceUnavailableExceptionSchema(BaseModel):
    message: str
    status_code: int = 503
    type: str = "ServiceUnavailable"
