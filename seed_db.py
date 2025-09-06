from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Student, CounsellingNote, IncomingMail, DB_FILE
import random
from datetime import datetime, timedelta

# (Configuration and templates remain the same)
NUM_STUDENTS = 50
engine = create_engine(f'sqlite:///{DB_FILE}')
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()
MAJORS = ["Computer Science", "Psychology", "Business Administration", "Biology", "Mechanical Engineering", "Fine Arts"]
PERSONAS = ["High-achieving but anxious...", "Struggling with course load...", "Feeling isolated...", "First-generation student...", "Experiencing time management issues..."]
SESSION_TYPES = ["Academic Advising", "Career Counselling", "Personal Wellness", "Follow-up"]
NOTES_TEMPLATES = { "Academic Advising": "Student discussed feeling overwhelmed...", "Career Counselling": "Explored potential career paths...", "Personal Wellness": "Student expressed feelings of stress...", "Follow-up": "Checked in on progress..."}
NEXT_STEPS_TEMPLATES = { "Academic Advising": "Student will schedule a meeting...", "Career Counselling": "Student will draft a new resume...", "Personal Wellness": "Counsellor to email student...", "Follow-up": "Schedule another check-in..."}


def create_showcase_student():
    """Creates a specific student profile for the reply-generation showcase."""
    rohan = Student(name="Rohan Verma", email="rohan.verma@mpstme.edu.in", major="AI Engineering", year=4, persona="Ambitious student, well-prepared for MS applications but anxious about global events.")
    session.add(rohan)
    session.commit()
    note1 = CounsellingNote(student_id=rohan.id, session_date=datetime.utcnow() - timedelta(days=60), session_type="Career Counselling", notes="Discussed MS in AI abroad, shortlisted universities in US, Canada, UK.", next_steps="Finalize list and start SOP.")
    note2 = CounsellingNote(student_id=rohan.id, session_date=datetime.utcnow() - timedelta(days=20), session_type="Follow-up", notes="Reviewed SOP draft. Mentioned concerns about visa processes and political climates.", next_steps="Connect with alumni for experiences.")
    
    # --- NEW: Add Rohan's unreplied email to the database ---
    rohan_mail = IncomingMail(
        student_id=rohan.id,
        received_date=datetime.utcnow() - timedelta(days=2),
        subject="Worried about MS plans",
        body="Dear Counsellor,\n\nHope you are doing well.\n\nWe spoke a few weeks ago about my MS in AI applications. I'm making good progress on my SOPs, but I'm getting really worried about the global situation. With all the news about changing visa policies in the US and UK, and the general political instability, I'm starting to second-guess if this is the right time to go abroad. It's causing me a lot of stress.\n\nIs this something we could talk about?\n\nThanks,\nRohan Verma"
    )
    session.add_all([note1, note2, rohan_mail])
    session.commit()
    print("Showcase student 'Rohan Verma' and his unreplied email added.")


def create_random_students_and_mails():
    """Creates random student profiles and adds unreplied emails to some of them."""
    students_to_create = []
    for _ in range(NUM_STUDENTS):
        students_to_create.append(Student(name=fake.name(), email=fake.email(), major=random.choice(MAJORS), year=random.randint(1, 4), persona=random.choice(PERSONAS)))
    session.bulk_save_objects(students_to_create)
    session.commit()

    all_students = session.query(Student).filter(Student.name != "Rohan Verma").all()
    
    # Add unreplied emails to a subset of random students
    students_with_mail = random.sample(all_students, k=10)
    for student in students_with_mail:
        mail = IncomingMail(
            student_id=student.id,
            received_date=datetime.utcnow() - timedelta(days=random.randint(1, 5)),
            subject=random.choice(["Question about my final project", "Feeling overwhelmed", "Need to change a course"]),
            body=fake.paragraph(nb_sentences=5)
        )
        session.add(mail)
    session.commit()
    print(f"Added unreplied emails to {len(students_with_mail)} random students.")


def create_mock_data():
    if session.query(Student).count() > 0:
        print("Database already contains data. Aborting.")
        return

    create_showcase_student()
    create_random_students_and_mails()
    
    try:
        session.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_mock_data()