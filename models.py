from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from database import Base
from sqlalchemy.sql import func

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())