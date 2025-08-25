import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import os

# Define the database file name
DB_FILE = "crm_database.db"

# --- Declarative Base ---
# The Base which all our data models will inherit from
Base = declarative_base()

# --- Data Models (Tables) ---

class Customer(Base):
    """
    Represents a customer in the CRM.
    """
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    company = Column(String(100))
    persona = Column(String(255), comment="A brief description of the customer's profile, e.g., 'Tech-savvy CEO'")
    
    # This creates a one-to-many relationship with InteractionHistory
    interactions = relationship("InteractionHistory", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', email='{self.email}')>"

class InteractionHistory(Base):
    """
    Represents a single interaction with a customer.
    """
    __tablename__ = 'interaction_history'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    interaction_type = Column(String(50), comment="e.g., 'Email Sent', 'Purchase', 'Support Ticket'")
    content = Column(Text, comment="The body of the email or a note about the interaction")
    interaction_date = Column(DateTime, default=datetime.datetime.utcnow)

    # This links the interaction back to the Customer object
    customer = relationship("Customer", back_populates="interactions")

    def __repr__(self):
        return f"<InteractionHistory(id={self.id}, type='{self.interaction_type}', customer_id={self.customer_id})>"

# --- Database Creation Function ---

def create_database():
    """Creates the SQLite database and tables if they don't already exist."""
    # Check if the database file already exists to avoid overwriting
    if os.path.exists(DB_FILE):
        print(f"Database '{DB_FILE}' already exists.")
        return

    # The engine is the entry point to the database.
    # 'echo=True' will print all the SQL statements it executes.
    engine = create_engine(f'sqlite:///{DB_FILE}', echo=True)
    
    print(f"Creating database '{DB_FILE}'...")
    # This command creates all the tables defined in our models.
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")

# --- Main Execution ---

if __name__ == "__main__":
    # This block will only run when the script is executed directly
    create_database()