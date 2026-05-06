from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NoteCreate(BaseModel):
    category: str = Field(max_length=50)
    message_body: str = Field(max_length=1000)
    tag: Optional[str] = Field(default=None, max_length=50)

class NoteUpdate(BaseModel):
    category: Optional[str] = Field(default=None, max_length=50)
    message_body: Optional[str] = Field(default=None, max_length=1000)
    tag: Optional[str] = Field(default=None, max_length=50)

class EventCreate(BaseModel):
    category: str = Field(max_length=50)
    message_body: str = Field(max_length=1000)
    classification: str = Field(max_length=50)
    tag: Optional[str] = Field(default=None, max_length=50)
    scheduled_at: datetime
    notification_at: Optional[datetime]= Field(default=None)

class EventUpdate(BaseModel):
    category: Optional[str] = Field(default=None, max_length=50)
    message_body: Optional[str] = Field(default=None, max_length=1000)
    classification: Optional[str] = Field(default=None, max_length=50)
    tag: Optional[str] = Field(default=None, max_length=50)
    scheduled_at: Optional[datetime] = Field(default= None)
    notification_at: Optional[datetime] = Field(default=None)
    status: Optional[str] = Field(default=None) # idéia aqui no futuro não é permitir que o usuário insira a informção, mas opte por alternativas fornecidas (1 - Finished | 2 - Canceled)
