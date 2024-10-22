from enum import Enum


class EventType(Enum):

    def __str__(self):
        return str(self.value)


class RPCPayloadType(Enum):
    GET_INTERVIEW_DETAILS = "GET_INTERVIEW_DETAILS"
    GET_USER_RESUME = "GET_USER_RESUME"

    def __str__(self):
        return str(self.value)
