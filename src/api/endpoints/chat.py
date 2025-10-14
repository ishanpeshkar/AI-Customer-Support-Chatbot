# src/api/endpoints/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as SQLModelSession, select, SQLModel
from typing import List, Optional # <-- Import Optional

from src.db.database import get_session
from src.db.models import Session, Message
from src.services import llm_handler

router = APIRouter()

class MessageCreate(SQLModel):
    content: str

class MessageRead(SQLModel):
    id: int
    content: str
    sender: str

class SessionRead(SQLModel):
    id: int
    summary: Optional[str] = None
# -------------------------------------


@router.post("/sessions/", response_model=SessionRead, status_code=201)
def create_session(db: SQLModelSession = Depends(get_session)):
    new_session = Session()
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/sessions/{session_id}/messages/", response_model=List[MessageRead])
def get_messages_for_session(session_id: int, db: SQLModelSession = Depends(get_session)):
    messages = db.exec(select(Message).where(Message.session_id == session_id)).all()
    return messages


@router.post("/sessions/{session_id}/messages/", response_model=MessageRead)
def post_message(session_id: int, message_data: MessageCreate, db: SQLModelSession = Depends(get_session)):
    """
    Posts a new message to a session and gets a bot response from the LLM.
    """
    # 1. Save the user's message
    user_message = Message(session_id=session_id, content=message_data.content, sender="user")
    db.add(user_message)
    db.commit()

    # 2. Retrieve the full conversation history
    history_statement = select(Message).where(Message.session_id == session_id).order_by(Message.timestamp)
    conversation_history = db.exec(history_statement).all()

    # 3. Get a response from the LLM
    bot_response_content = llm_handler.generate_bot_response(conversation_history)

    # 4. Save the bot's response
    bot_message = Message(session_id=session_id, content=bot_response_content, sender="bot")
    db.add(bot_message)
    db.commit()
    db.refresh(bot_message)
    
    return bot_message

# --- NEW: Summarization Endpoint ---
@router.post("/sessions/{session_id}/summarize", response_model=SessionRead)
def summarize_session(session_id: int, db: SQLModelSession = Depends(get_session)):
    """
    Generates a summary for the session and stores it.
    """
    session = db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Retrieve conversation history
    history_statement = select(Message).where(Message.session_id == session_id).order_by(Message.timestamp)
    conversation_history = db.exec(history_statement).all()

    if not conversation_history:
        raise HTTPException(status_code=400, detail="Cannot summarize an empty session.")
    
    # Generate summary
    summary_text = llm_handler.summarize_conversation(conversation_history)

    # Save summary to the database
    session.summary = summary_text
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session
# -----------------------------------