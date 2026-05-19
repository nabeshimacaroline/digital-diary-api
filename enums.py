from enum import Enum

class StatusEvent(Enum):
    SCHEDULED = "scheduled"
    FINISHED = "finished"
    CANCELED = "canceled"