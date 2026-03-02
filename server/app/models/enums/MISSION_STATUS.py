from enum import Enum

class MissionStatus(Enum):
    NOT_STARTED = "not_started"
    INCORRECT = "incorrect"
    CORRECT = "correct"