from enum import Enum

class FillStatus(Enum):
    def __str__(self):
        return str(self.value)
    OFFLINE = 0
    READY = 1
    PURGING = 2
    FILLING = 3
    COMPLETE = 4
    CLEANING = 10
    CALIBRATING = 20
    ERROR = 50
