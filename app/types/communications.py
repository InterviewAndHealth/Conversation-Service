from enum import StrEnum


class EventType(StrEnum):

    def __str__(self):
        return str(self.value)


class RPCPayloadType(StrEnum):
    GET_INTERVIEW_DETAILS = "GET_INTERVIEW_DETAILS"
    GET_USER_RESUME = "GET_USER_RESUME"
