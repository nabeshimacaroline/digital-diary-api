from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from database import Base
from sqlalchemy.sql import func

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    category = Column(String(50))
    message_body = Column(Text)
    tag = Column(String(50))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

#class Event(Base):
#    __tablename__ = "events"
#    id = Column(Integer, primary_key=True, index=True)
#    note_id = Column(Integer, ForeignKey("notes.id"))
#    classification = Column(String(50))
#    scheduled_at = Column(DateTime)
#    status = Column(String(50))
#    notification_at = Column(DateTime)
#    is_notify = Column(Boolean)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    category = Column(String(50))
    message_body = Column(Text)
    classification = Column(String(50))
    tag = Column(String(50))
    scheduled_at = Column(DateTime)
    status = Column(String(50))
    notification_at = Column(DateTime)
    is_notify = Column(Boolean)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())