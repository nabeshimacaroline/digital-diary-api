from pydantic import BaseModel, Field
from typing import Optional

class NoteCreate(BaseModel):
    category: str = Field(max_length=50)
    message_body: str = Field(max_length=1000)
    tag: Optional[str] = Field(default=None, max_length=50)

class NoteUpdate(BaseModel):
    category: Optional[str] = Field(default=None, max_length=50)
    message_body: Optional[str] = Field(default=None, max_length=1000)
    tag: Optional[str] = Field(default=None, max_length=50)