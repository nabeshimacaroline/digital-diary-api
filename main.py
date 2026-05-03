from sqlalchemy.orm import Session
import models
from fastapi import FastAPI, Depends
from models import Note
from database import engine, SessionLocal
from schemas import NoteCreate

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
