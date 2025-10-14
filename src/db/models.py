from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
import datetime

class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    summary: Optional[str] = None

    messages: List["Message"] = Relationship(back_populates="session")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="session.id")
    content: str
    sender: str  # "user" or "bot"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    session: Session = Relationship(back_populates="messages")