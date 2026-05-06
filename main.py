from sqlalchemy.orm import Session
import models
from fastapi import FastAPI, Depends, HTTPException
from models import Note, Event
from database import engine, SessionLocal
from schemas import NoteCreate, NoteUpdate, EventCreate
from datetime import datetime, timezone

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        status = "Scheduled"
        )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@app.get("/events/")
def list_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    now = datetime.now(timezone.utc)

    for event in events:
        scheduled = event.scheduled_at

        # 1. Blindagem de segurança do fuso horário para a leitura
        if scheduled is not None and scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        # 2. A checagem do correto   
        if event.status == "Scheduled" and scheduled < now:
            event.status = "Pending"

    return events

@app.get("/events/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    now = datetime.now(timezone.utc)
    scheduled = event.scheduled_at

    if scheduled is not None and scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
         
    if event.status == "Scheduled" and scheduled < now:
        event.status = "Pending"
    
    return event