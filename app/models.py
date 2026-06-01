from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import StatusEvent

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    user = relationship("User")
    created_at = Column(DateTime, server_default=func.now())
    category_id = Column(Integer, ForeignKey("categories.id"), index=True, nullable=False)
    category = relationship("Category")
    message_body = Column(Text)
    tag = Column(String(50))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    user = relationship("User")
    note_id = Column(Integer, ForeignKey("notes.id"), index=True, nullable=True)
    note = relationship("Note")
    created_at = Column(DateTime, server_default=func.now())
    category_id = Column(Integer, ForeignKey("categories.id"), index=True, nullable=False)
    category = relationship("Category")
    message_body = Column(Text)
    classification = Column(String(50))
    tag = Column(String(50))
    scheduled_at = Column(DateTime)
    status = Column(SQLEnum(StatusEvent, native_enum=False, name="status_event"), nullable=False, default=StatusEvent.SCHEDULED)
    notification_at = Column(DateTime)
    is_notify = Column(Boolean)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)   
    hashed_password = Column(String(255), nullable=False) 
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
