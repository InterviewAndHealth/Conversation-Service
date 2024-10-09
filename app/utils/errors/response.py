from .exceptions import *

BadRequestExceptionResponse = BadRequestException400.response()
UnauthorizedExceptionResponse = UnauthorizedException401.response()
NotFoundExceptionResponse = NotFoundException404.response()
RequestTimeoutExceptionResponse = RequestTimeoutException408.response()
InternalServerErrorExceptionResponse = InternalServerErrorException500.response()
ServiceUnavailableExceptionResponse = ServiceUnavailableException503.response()
