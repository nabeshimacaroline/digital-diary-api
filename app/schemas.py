from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from app.enums import StatusEvent

# ---------------------------------------------------------------
#                            NOTE
# ---------------------------------------------------------------

class NoteCreate(BaseModel):
    category: str = Field(max_length=50)
    message_body: str = Field(max_length=1000)
    tag: Optional[str] = Field(default=None, max_length=50)

class NoteUpdate(BaseModel):
    category: Optional[str] = Field(default=None, max_length=50)
    message_body: Optional[str] = Field(default=None, max_length=1000)
    tag: Optional[str] = Field(default=None, max_length=50)

class NoteResponse(BaseModel):
    id: int
    created_at: datetime
    category: str
    message_body: str
    tag: Optional[str]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("category", mode="before")
    @classmethod
    def extract_category_name(cls, v):
        if hasattr(v, "name"):
            return v.name
        return v

# ---------------------------------------------------------------
#                            EVENT
# ---------------------------------------------------------------

class EventCreate(BaseModel):
    # se Event for criado a partir de uma Note existente, passar note_id
    note_id: Optional[int] = Field(default=None)
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
    note_id: Optional[int] = Field(default=None)
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

    @field_validator("category", mode="before")
    @classmethod
    def extract_category_name(cls, v):
        if hasattr(v, "name"):
            return v.name
        return v