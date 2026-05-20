from sqlalchemy.orm import Session
from app import models
from fastapi import FastAPI, Depends, HTTPException
from app.models import Note, Event
from app.database import engine, get_db
from app.schemas import NoteCreate, NoteUpdate, EventCreate, EventUpdate, EventResponse
from datetime import datetime, timezone
from app.enums import StatusEvent

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
     return {"message": "Digital Diary API is alive!"}

@app.post("/notes/")
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Note(
        category=payload.category,
        message_body=payload.message_body,
        tag=payload.tag
        )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@app.get("/notes/")
def list_notes(db: Session = Depends(get_db)):
    notes = db.query(Note).all()
    return notes

@app.get("/notes/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.patch("/notes/{note_id}")
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    # buscar e validar
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    #atualizar dados
    update_data = payload.model_dump(exclude_unset=True) # Pega só o que o usuário enviou
    for key, value in update_data.items():
        setattr(note, key, value) # Substitui o valor antigo pelo novo no objeto da nota
    
    #salvar e retornar
    db.commit()
    db.refresh(note)
    return note

@app.delete("/notes/{note_id}")
def delete_note (note_id: int, db: Session = Depends(get_db)):
    # buscar e validar
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    #deletar os dados
    db.delete(note)
    
    #salvar
    db.commit()
    return {"message": "Note deleted successfully"}

@app.post("/events/")
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

@app.get("/events/", response_model=list[EventResponse])
def list_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    now = datetime.now(timezone.utc)

    for event in events:
        scheduled = event.scheduled_at

        # 1. Blindagem de segurança do fuso horário para a leitura
        if scheduled is not None and scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        # 2. A checagem do correto   
        if event.status == StatusEvent.SCHEDULED and scheduled < now:
            event.status = "Pending"

    return events

@app.get("/events/{event_id}", response_model=EventResponse)
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

@app.patch("/events/{event_id}")
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    # buscar e validar
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
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

@app.delete("/events/{event_id}")
def delete_event (event_id: int, db: Session = Depends(get_db)):
    # buscar e validar
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    #deletar os dados
    db.delete(event)
    
    #salvar
    db.commit()
    return {"message": "Event deleted successfully"}