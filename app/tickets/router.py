from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.tickets.schemas import TicketCreate, TicketResponse
from app.tickets.service import create_ticket


router = APIRouter(tags=["Tickets"])


@router.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
):
    return create_ticket(db, ticket)