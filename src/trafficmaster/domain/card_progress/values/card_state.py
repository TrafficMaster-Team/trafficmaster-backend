from enum import StrEnum


class CardState(StrEnum):
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    RELEARNING = "relearning"
