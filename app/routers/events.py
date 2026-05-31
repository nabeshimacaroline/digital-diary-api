from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from app.database import get_db
from app.models import Event, Category, User
from app.schemas import EventCreate, EventUpdate, EventResponse
from app.enums import StatusEvent
from app.utils import clean_and_normalize_label
from app.security import get_current_user

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/", response_model=EventResponse, status_code=201)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    # 1. Higienizar a categoria
    clean_category_name = payload.category
    
    # 2. Buscar categoria no Banco
    db_category = db.query(Category).filter(Category.name == clean_category_name).first()

    # 3. Se não existir, cria uma.
    if not db_category:
        db_category = Category(name=clean_category_name)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
    
    # 5. definição do tempo
    now = datetime.now(timezone.utc)
    scheduled = payload.scheduled_at
    notification = payload.notification_at

    #6. validação
    if scheduled < now:
        raise HTTPException(status_code=400, detail="Scheduled cannot be a date in the past.")
    
    if notification is not None and notification > scheduled:
        raise HTTPException(status_code=400, detail="Notification cannot be set on a date later than scheduled.")
    
    # 7. Preparando os dados para Event
    event_data = payload.model_dump(exclude={"category"}) #pegar tudo do payload, excluindo a string "category"
    event_data["category_id"] = db_category.id

    new_event = Event(**event_data, user_id=current_user.id)
        
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@router.get("/", response_model=list[EventResponse])
def list_events(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    now = datetime.now(timezone.utc)
    query = db.query(Event).filter(Event.user_id == current_user.id)

    if category:
        clean_category_name = clean_and_normalize_label(category)
        query = query.filter(Event.category.has(name=clean_category_name))

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
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
        ).first()
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
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    # buscar e validar
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
        ).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status in [StatusEvent.FINISHED, StatusEvent.CANCELED]:
        raise HTTPException(status_code=400, detail="Finished events or Canceled events cannot be edited")
    
    # Pega só o que o usuário enviou
    update_data = payload.model_dump(exclude_unset=True) 

    # Determinar se há envio de categoria
    if "category" in update_data and update_data["category"]:
        # Receber categoria normalizada
        clean_category_name = update_data["category"]

        # Buscar ou cria categoria no banco
        db_category = db.query(Category).filter(Category.name == clean_category_name).first()
        if not db_category:
            db_category = Category(name=clean_category_name)
            db.add(db_category)
            db.commit()
            db.refresh(db_category)

        #5 Remover a string e inserir o id
        del update_data["category"]
        update_data["category_id"] = db_category.id

    # --- inicio da validação de tempo---
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
    if "scheduled_at" in update_data:
        now = datetime.now(timezone.utc)
        if final_scheduled < now:
            raise HTTPException (status_code=400, detail="Scheduled cannot be a date in the past")
    
    # --- final da validação ---

    for key, value in update_data.items():
        setattr(event, key, value) # Substitui o valor antigo pelo novo no objeto da nota
    
    #salvar e retornar
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
def delete_event (
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    # buscar e validar
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
        ).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status in [StatusEvent.FINISHED, StatusEvent.CANCELED]:
        raise HTTPException(status_code=400, detail="Finished events or Canceled events cannot be deleted" )
    
    #deletar os dados
    db.delete(event)
    
    #salvar
    db.commit()
    return {"message": "Event deleted successfully"}