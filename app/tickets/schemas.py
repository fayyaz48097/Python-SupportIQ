
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.tickets.enums import TicketStatus


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject: str = Field(min_length=3, max_length=150)
    message: str = Field(min_length=10, max_length=5000)


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    message: str
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
