# filename: /app/errors.py
from enum import Enum
from pydantic import BaseModel

class GlobalErrorType(str, Enum):
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EASTER_EGG_FOUND = "Trying to hack Broh?"
    # add more as NexusFest grows

class ErrorPayload(BaseModel):
    type: GlobalErrorType
    message: str
    status: int