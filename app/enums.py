from enum import Enum

class StatusEvent(str, Enum):
    SCHEDULED = "scheduled"
    FINISHED = "finished"
    CANCELED = "canceled"