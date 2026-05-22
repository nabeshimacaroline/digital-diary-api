from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventUpdate, EventResponse
from app.enums import StatusEvent

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/")
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    #definição do tempo
    now = datetime.now(timezone.utc)
    scheduled = payload.scheduled_at
    notification = payload.notification_at

    #validação
    if scheduled < now:
        raise HTTPException(status_code=400, detail="Scheduled cannot be a date in the past.")
    
    if notification is not None and notification > scheduled:
        raise HTTPException(status_code=400, detail="Notification cannot be set on a date later than scheduled.")

    event = Event(
        category=payload.category,
        message_body=payload.message_body,
        classification=payload.classification,
        tag=payload.tag,
        scheduled_at=payload.scheduled_at,
        notification_at=payload.notification_at,
        )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get("/", response_model=list[EventResponse])
def list_events(category: Optional[str] = Query(None),
                status: Optional[str] = Query(None),
                search: Optional[str] = Query(None),
                start_date: Optional[datetime] = Query(None),
                end_date: Optional[datetime] = Query(None),
                skip: int = Query(0, ge=0),
                limit: int = Query(10, ge=1, le=100),
                db: Session = Depends(get_db)
                ):
    now = datetime.now(timezone.utc)
    query = db.query(Event)

    if category:
        query = query.filter(Event.category == category)

    if status:
        status = status.lower()
        if status == "pending":
            query = query.filter(Event.status == StatusEvent.SCHEDULED, Event.scheduled_at < now)

        elif status == "scheduled":
            query = query.filter(Event.status == StatusEvent.SCHEDULED, Event.scheduled_at > now)

        else:    
            query = query.filter(Event.status == status)
    
    if search:
        query = query.filter(Event.message_body.ilike(f"%{search}%"))
    
    if start_date:
        query = query.filter(Event.scheduled_at >= start_date)

    if end_date:
        query = query.filter(Event.scheduled_at <= end_date)

    events = query.order_by(Event.scheduled_at.desc()).offset(skip).limit(limit).all()

    for event in events:
        scheduled = event.scheduled_at

        # 1. Blindagem de segurança do fuso horário para a leitura
        if scheduled is not None and scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        # 2. A checagem do correto   
        if event.status == StatusEvent.SCHEDULED and scheduled < now:
            event.status = "Pending"

    return events

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    now = datetime.now(timezone.utc)
    scheduled = event.scheduled_at

    if scheduled is not None and scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
         
    if event.status == StatusEvent.SCHEDULED and scheduled < now:
        event.status = "Pending"
    
    return event

@router.patch("/{event_id}")
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    # buscar e validar
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status in [StatusEvent.FINISHED, StatusEvent.CANCELED]:
        raise HTTPException(status_code=400, detail="Finished events or Canceled events cannot be edited")
    
    # Pega só o que o usuário enviou
    update_data = payload.model_dump(exclude_unset=True) 

    # --- inicio da validação ---
    # previsão de futuro
    final_scheduled = update_data.get("scheduled_at", event.scheduled_at)
    final_notification = update_data.get("notification_at", event.notification_at)

    #blindagem
    if final_scheduled is not None and final_scheduled.tzinfo is None:
        final_scheduled = final_scheduled.replace(tzinfo=timezone.utc)
    if final_notification is not None and final_notification.tzinfo is None:
        final_notification = final_notification.replace(tzinfo=timezone.utc)
    
    # regras de negocio
    #regra 1 - data de notificação não pode ser maior que a data do evento
    if final_notification is not None and final_notification > final_scheduled:
        raise HTTPException(status_code=400, detail="Notification cannot be set on a date later than scheduled.")

    #regra 2 - se o usuário estiver alterando uma data, ela não pode estar no passado
    if final_scheduled in update_data:
        now = datetime.now(timezone.utc)
        if final_scheduled < now:
            raise HTTPException (status_code=400, details="Scheduled cannot be a date in the past")
    
    # --- final da validação ---

    for key, value in update_data.items():
        setattr(event, key, value) # Substitui o valor antigo pelo novo no objeto da nota
    
    #salvar e retornar
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
def delete_event (event_id: int, db: Session = Depends(get_db)):
    # buscar e validar
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status in [StatusEvent.FINISHED, StatusEvent.CANCELED]:
        raise HTTPException(status_code=400, detail="Finished events or Canceled events cannot be deleted" )
    
    #deletar os dados
    db.delete(event)
    
    #salvar
    db.commit()
    return {"message": "Event deleted successfully"}