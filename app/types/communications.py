from enum import Enum


class EventType(Enum):
    pass


class RPCPayloadType(Enum):
    GET_INTERVIEW_DETAILS = "GET_INTERVIEW_DETAILS"
    GET_USER_RESUME = "GET_USER_RESUME"
