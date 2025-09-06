import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
import os

DB_FILE = "counselling_database.db"
Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    major = Column(String(100))
    year = Column(Integer)
    persona = Column(String(255))
    
    notes = relationship("CounsellingNote", back_populates="student", cascade="all, delete-orphan")
    incoming_mails = relationship("IncomingMail", back_populates="student", cascade="all, delete-orphan")

class CounsellingNote(Base):
    __tablename__ = 'counselling_notes'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    session_date = Column(DateTime, default=datetime.datetime.utcnow)
    session_type = Column(String(100))
    notes = Column(Text)
    next_steps = Column(Text)
    student = relationship("Student", back_populates="notes")

# --- NEW: Table for incoming student emails ---
class IncomingMail(Base):
    """Represents an email received from a student that needs a reply."""
    __tablename__ = 'incoming_mails'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    received_date = Column(DateTime, default=datetime.datetime.utcnow)
    subject = Column(Text)
    body = Column(Text)
    replied = Column(Boolean, default=False) # --- NEW: Status to track replies ---
    
    student = relationship("Student", back_populates="incoming_mails")

def create_database():
    if os.path.exists(DB_FILE):
        print(f"Database '{DB_FILE}' already exists.")
        return
    engine = create_engine(f'sqlite:///{DB_FILE}', echo=True)
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")

if __name__ == "__main__":
    create_database()