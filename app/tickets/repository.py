from sqlalchemy.orm import Session

from app.tickets.models import Ticket
from app.tickets.schemas import TicketCreate


def create(db: Session, ticket_data: TicketCreate) -> Ticket:
    ticket = Ticket(
        subject=ticket_data.subject,
        message=ticket_data.message,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket