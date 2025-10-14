# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <-- IMPORT THIS
from src.db.database import create_db_and_tables
from src.api.endpoints import chat

app = FastAPI(
    title="AI Customer Support Bot",
    description="A standout project for a job hiring task.",
    version="1.0.0"
)

# --- ADD THIS MIDDLEWARE CONFIGURATION ---
# This allows your frontend (running on any domain) to communicate with your backend.
# For production, you would restrict origins to your actual frontend's domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# -----------------------------------------

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Welcome to the AI Customer Support Bot API!"}