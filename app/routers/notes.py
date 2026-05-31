from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models import Note, Category, User
from app.schemas import NoteCreate, NoteUpdate, NoteResponse
from app.utils import clean_and_normalize_label
from app.security import get_current_user

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model=NoteResponse, status_code=201)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    #1 Recebendo a categoria já normalizada
    clean_category_name = payload.category

    #2 Buscar categoria no banco
    db_category = db.query(Category).filter(Category.name == clean_category_name).first()

    #3 Se não existir criar uma:
    if not db_category:
        db_category = Category(name=clean_category_name)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)

    #4 Preparando pacote de dados
    note_data = payload.model_dump(exclude={"category"})
    note_data["category_id"] = db_category.id

    new_note = Note(**note_data, user_id=current_user.id)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.get("/", response_model=list[NoteResponse])
def list_notes(
            category: Optional[str] = Query(None),
            search: Optional[str] = Query(None),
            start_date: Optional[datetime] = Query(None),
            end_date: Optional[datetime] = Query(None),
            skip: int = Query(0, ge=0),
            limit: int = Query(10, ge=1, le=100),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)
            ):
    
    query = db.query(Note).filter(Note.user_id == current_user.id)

    if category:
        clean_category_name = clean_and_normalize_label(category)
        query = query.filter(Note.category.has(name=clean_category_name))
    
    if search:
        query = query.filter(Note.message_body.ilike(f"%{search}%"))
    
    if start_date:
        query = query.filter(Note.created_at >= start_date)

    if end_date:
        query = query.filter(Note.created_at <= end_date)
    
    notes = query.order_by(Note.created_at.desc()).offset(skip).limit(limit).all()
    return notes

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
        note_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
        ):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
        ).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.patch("/{note_id}")
def update_note(
            note_id: int,
            payload: NoteUpdate,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    #1 buscar e validar
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
        ).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    #2 Pega só o que o usuário mandou
    update_data = payload.model_dump(exclude_unset=True)

    #3 Determinar se há envio de categoria
    if "category" in update_data and update_data["category"]:
        #4 Higienizar a categoria
        clean_category_name = update_data["category"]

        #4 Buscar ou cria categoria no banco
        db_category = db.query(Category).filter(Category.name == clean_category_name).first()
        if not db_category:
            db_category = Category(name=clean_category_name)
            db.add(db_category)
            db.commit()
            db.refresh(db_category)

        #5 Remover a string e inserir o id
        del update_data["category"]
        update_data["category_id"] = db_category.id

    for key, value in update_data.items():
        setattr(note, key, value) # Substitui dados limpos no objeto da nota
    
    #salvar e retornar
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}")
def delete_note (
        note_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
        ):
    # buscar e validar
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
        ).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    #deletar os dados
    db.delete(note)
    
    #salvar
    db.commit()
    return {"message": "Note deleted successfully"}

