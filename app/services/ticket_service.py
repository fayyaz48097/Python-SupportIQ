
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate


def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:

    ticket = Ticket(
        subject=ticket_data.subject,
        message=ticket_data.message
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket
