from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Customer, InteractionHistory, DB_FILE
import random

# --- Configuration ---
NUM_CUSTOMERS = 50
INTERACTIONS_PER_CUSTOMER = 10

# --- Database Connection ---
engine = create_engine(f'sqlite:///{DB_FILE}')
Session = sessionmaker(bind=engine)
session = Session()

# --- Data Generation ---
fake = Faker()

def create_mock_data():
    """Generates and inserts mock data into the database."""
    
    # Check if data already exists
    if session.query(Customer).count() > 0:
        print("Database already contains data. Aborting seeding process.")
        return

    print("Seeding database with mock data...")
    customers = []
    for _ in range(NUM_CUSTOMERS):
        # Create a new customer
        customer = Customer(
            name=fake.name(),
            email=fake.email(),
            company=fake.company(),
            persona=random.choice([
                "Tech-savvy CEO",
                "Non-technical Marketing Manager",
                "Cautious Financial Analyst",
                "Early Adopter Startup Founder",
                "Long-time Loyal User"
            ])
        )
        customers.append(customer)
    
    # Bulk insert all customers
    session.bulk_save_objects(customers)
    
    # Create interactions for each customer
    all_customers = session.query(Customer).all()
    for customer in all_customers:
        for _ in range(random.randint(5, INTERACTIONS_PER_CUSTOMER)):
            interaction = InteractionHistory(
                customer_id=customer.id,
                interaction_type=random.choice(["Email Sent", "Purchase", "Support Ticket", "Website Visit"]),
                content=fake.paragraph(nb_sentences=5)
            )
            session.add(interaction)
            
    # --- Commit Changes ---
    try:
        session.commit()
        print(f"Successfully added {NUM_CUSTOMERS} customers and their interactions.")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_mock_data()