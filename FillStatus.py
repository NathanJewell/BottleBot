from enum import Enum

class FillStatus(Enum):
    OFFLINE = 0
    READY = 1
    PURGING = 2
    FILLING = 3
    COMPLETE = 4
    CLEANING = 10
    CALIBRATING = 20
    TESTING = 30
    ERROR = 50
