from sqlalchemy.orm import Session

from app.tickets import repository
from app.tickets.models import Ticket
from app.tickets.schemas import TicketCreate


def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
    return repository.create(db, ticket_data)