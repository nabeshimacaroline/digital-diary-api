from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enums import StatusEvent

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
    status: Optional[StatusEvent] = Field(default=None) # idéia aqui no futuro não é permitir que o usuário insira a informção, mas opte por alternativas fornecidas (1 - Finished | 2 - Canceled)

class EventResponse(BaseModel):
    id: int
    created_at: datetime
    category: str
    message_body: str
    classification: str
    tag: Optional[str]
    scheduled_at: datetime
    status: StatusEvent | str
    notification_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)