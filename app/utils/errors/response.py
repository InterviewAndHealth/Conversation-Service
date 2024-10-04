from .exceptions import *

BadRequestExceptionResponse = BadRequestException.response()
UnauthorizedExceptionResponse = UnauthorizedException.response()
NotFoundExceptionResponse = NotFoundException.response()
RequestTimeoutExceptionResponse = RequestTimeoutException.response()
InternalServerErrorExceptionResponse = InternalServerErrorException.response()
ServiceUnavailableExceptionResponse = ServiceUnavailableException.response()
