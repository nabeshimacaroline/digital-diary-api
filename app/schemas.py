from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr, model_validator
from typing import Optional
from datetime import datetime
from app.enums import StatusEvent
from app.utils import clean_and_normalize_label

# ---------------------------------------------------------------
#                            NOTE
# ---------------------------------------------------------------

class NoteCreate(BaseModel):
    category: str = Field(max_length=50)
    message_body: str = Field(max_length=1000)
    tag: Optional[str] = Field(default=None, max_length=50)

    @field_validator("category", mode="before")
    @classmethod
    def _normalize_category(cls, v):
        if v is None:
            raise ValueError("category is required")
        
        normalized = clean_and_normalize_label(v)
        if not normalized:
            raise ValueError("category inválida após normalização")
        return normalized


class NoteUpdate(BaseModel):
    category: Optional[str] = Field(default=None, max_length=50)
    message_body: Optional[str] = Field(default=None, max_length=1000)
    tag: Optional[str] = Field(default=None, max_length=50)

    @field_validator("category", mode="before")
    @classmethod
    def _normalize_category(cls, v):
        if v is None:
            return None
        
        normalized = clean_and_normalize_label(v)
        if not normalized:
            raise ValueError("category inválida após normalização")
        return normalized

class NoteResponse(BaseModel):
    id: int
    user_id: int
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

    @field_validator("category", mode="before")
    @classmethod
    def _normalize_category(cls, v):
        if v is None:
            raise ValueError("category is required")
        
        normalized = clean_and_normalize_label(v)
        if not normalized:
            raise ValueError("category inválida após normalização")
        return normalized

class EventUpdate(BaseModel):
    category: Optional[str] = Field(default=None, max_length=50)
    message_body: Optional[str] = Field(default=None, max_length=1000)
    classification: Optional[str] = Field(default=None, max_length=50)
    tag: Optional[str] = Field(default=None, max_length=50)
    scheduled_at: Optional[datetime] = Field(default= None)
    notification_at: Optional[datetime] = Field(default=None)
    status: Optional[StatusEvent] = Field(default=None) # idéia aqui no futuro não é permitir que o usuário insira a informção, mas opte por alternativas fornecidas (1 - Finished | 2 - Canceled)

    @field_validator("category", mode="before")
    @classmethod
    def _normalize_category(cls, v):
        if v is None:
            return None
        
        normalized = clean_and_normalize_label(v)
        if not normalized:
            raise ValueError("category inválida após normalização")
        return normalized

class EventResponse(BaseModel):
    id: int
    user_id: int
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
    
# ---------------------------------------------------------------
#                            USER
# ---------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=100)
    username: str = Field(..., max_length=50) # Obrigatório, igual ao banco
    password: str = Field(..., min_length=8, max_length=50)
    confirm_password: str = Field(..., min_length=8, max_length=50)

    # O segurança verificando se as duas senhas batem
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("As senhas não coincidem.")
        return self
    
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
   