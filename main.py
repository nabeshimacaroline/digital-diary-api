from sqlalchemy.orm import Session
import models
from fastapi import FastAPI, Depends, HTTPException
from models import Note
from database import engine, SessionLocal
from schemas import NoteCreate, NoteUpdate

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