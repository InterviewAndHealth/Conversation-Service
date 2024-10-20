from .exceptions import *

BadRequestResponse = BadRequestException400.response()
UnauthorizedResponse = UnauthorizedException401.response()
NotFoundResponse = NotFoundException404.response()
RequestTimeoutResponse = RequestTimeoutException408.response()
InternalServerErrorResponse = InternalServerErrorException500.response()
ServiceUnavailableResponse = ServiceUnavailableException503.response()
