import os
import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Get the database URL, host, and port from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
HOST = os.getenv("HOST", "127.0.0.1")  # Default host is 127.0.0.1 if not set
PORT = int(os.getenv("PORT", 8000))    # Default port is 8000 if not set

# Database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Event model
class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for input validation
class EventCreate(BaseModel):
    event_type: str
    timestamp: datetime

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to report an event
@app.post("/report")
async def report_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = Event(event_type=event.event_type, timestamp=event.timestamp)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return {"message": "Event recorded"}

# Main function to run the FastAPI server
def main():
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
