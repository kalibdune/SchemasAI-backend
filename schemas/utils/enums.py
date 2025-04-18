from enum import StrEnum


class TokenType(StrEnum):
    access = "access"
    refresh = "refresh"


class SenderType(StrEnum):
    ai = "ai"
    user = "user"
