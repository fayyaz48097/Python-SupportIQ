
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum as SQLAlchemyEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.tickets.enums import TicketStatus


def utc_now() -> datetime:
    """
    Return the current UTC time without timezone information.

    MySQL DATETIME does not preserve timezone information,
    so we consistently store UTC timestamps.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    subject: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[TicketStatus] = mapped_column(
        SQLAlchemyEnum(
            TicketStatus,
            name="ticket_status",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
            validate_strings=True,
        ),
        default=TicketStatus.RECEIVED,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
