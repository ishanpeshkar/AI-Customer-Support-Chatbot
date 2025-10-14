
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <-- IMPORT THIS
from src.db.database import create_db_and_tables
from src.api.endpoints import chat

app = FastAPI(
    title="AI Customer Support Bot",
    description="A standout project for a job hiring task.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
# -----------------------------------------

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Welcome to the AI Customer Support Bot API!"}