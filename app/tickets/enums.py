from enum import Enum


class TicketStatus(str, Enum):
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"