#main code isme hai 
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Student, CounsellingNote, IncomingMail, DB_FILE
from llm_handler import load_model, generate_text
from langchain.prompts import PromptTemplate
from datetime import datetime, timezone

# --- Database Setup & AI Model Loading (No Changes) ---
engine = create_engine(f'sqlite:///{DB_FILE}')
Session = sessionmaker(bind=engine)
session = Session()

@st.cache_resource
def load_ai_model():
    return load_model()

# --- Helper Functions (No Changes) ---
def get_students():
    return session.query(Student).all()

def get_students_with_unreplied_mail():
    return session.query(Student).join(IncomingMail).filter(IncomingMail.replied == False).all()

def get_student_context(student):
    notes = session.query(CounsellingNote).filter_by(student_id=student.id).order_by(CounsellingNote.session_date.desc()).limit(5).all()
    context = f"**Student Name:** {student.name}\n\n"
    context += f"**Major:** {student.major} (Year {student.year})\n\n"
    context += f"**Counsellor's Persona Note:** {student.persona}\n\n"
    context += "**Recent Session History:**\n"
    if not notes: context += "- No session notes found.\n"
    for note in notes: context += f"- **Date:** {note.session_date.strftime('%Y-%m-%d')}\n  - **Type:** {note.session_type}\n  - **Notes:** {note.notes}\n  - **Next Steps:** {note.next_steps}\n"
    return context

# --- Prompt Generation (Combined into one function) ---
def create_dynamic_prompt(context, goal, incoming_email=None):
    if incoming_email: # Prompt for generating a reply
        template = """
        You are an expert and empathetic university counsellor. Your task is to write a supportive and professional *reply* to the student's email below.
        **STUDENT'S CONTEXT AND HISTORY:**
        {context}
        **INCOMING STUDENT EMAIL TO REPLY TO:**
        {incoming_email}
        Based on the student's history and their incoming email, write a reassuring and helpful reply now. Address their specific concerns directly.
        """
        prompt = PromptTemplate(template=template, input_variables=["context", "incoming_email"])
        return prompt.format(context=context, incoming_email=incoming_email)
    else: # Prompt for generating a new email
        template = """
        You are an expert and empathetic university counsellor. Your task is to write a supportive and professional proactive email to a student.
        **STUDENT'S CONTEXT AND HISTORY:**
        {context}
        **GOAL OF THIS EMAIL:**
        {goal}
        Based ONLY on the student's context and the specific goal, write the email now. Be encouraging and clear.
        """
        prompt = PromptTemplate(template=template, input_variables=["context", "goal"])
        return prompt.format(context=context, goal=goal)

# --- Streamlit UI ---
def main():
    st.set_page_config(layout="wide")
    st.title("🎓 Student Counselling AI Copilot")
    
    model, tokenizer, device = load_ai_model()

    # --- NEW: Mode Selection in Sidebar ---
    st.sidebar.title("Actions")
    app_mode = st.sidebar.radio("What would you like to do?", ["📧 Reply to Inbox", "✍️ Send New Email"])

    if app_mode == "📧 Reply to Inbox":
        render_inbox_mode(model, tokenizer, device)
    elif app_mode == "✍️ Send New Email":
        render_new_email_mode(model, tokenizer, device)

def render_inbox_mode(model, tokenizer, device):
    """Renders the UI for replying to unread emails."""
    st.header("📧 Inbox: Unreplied Student Emails")
    
    students_to_reply = get_students_with_unreplied_mail()
    
    if not students_to_reply:
        st.success("🎉 Inbox Zero! No pending replies.")
        return

    student_names = [s.name for s in students_to_reply]
    selected_student_name = st.selectbox("Select a Student to Reply To:", student_names)
    selected_student = next((s for s in students_to_reply if s.name == selected_student_name), None)

    if selected_student:
        unreplied_mail = session.query(IncomingMail).filter_by(student_id=selected_student.id, replied=False).first()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📬 Student's Incoming Email")
            if unreplied_mail:
                st.info(f"**From:** {selected_student.name}\n**Subject:** {unreplied_mail.subject}")
                st.text_area("Email Body", unreplied_mail.body, height=200, disabled=True)
            with st.expander("View Student History & Persona"):
                st.markdown(get_student_context(selected_student))
        
        with col2:
            st.subheader("🤖 AI-Generated Reply Draft")
            if unreplied_mail:
                if st.button("Generate AI Reply Draft"):
                    with st.spinner("Generating AI draft..."):
                        context_for_prompt = get_student_context(selected_student)
                        final_prompt = create_dynamic_prompt(context_for_prompt, "Reply to the student's email", unreplied_mail.body)
                        ai_reply = generate_text(model, tokenizer, device, final_prompt)
                        st.session_state['draft'] = ai_reply
                
                reply_text = st.text_area("Edit and finalize your reply:", value=st.session_state.get('draft', ''), height=250)

                if st.button("✔️ Send Reply & Archive"):
                    unreplied_mail.replied = True
                    new_note = CounsellingNote(student_id=selected_student.id, session_type="Email Reply Sent", notes=f"Replied to email with subject: '{unreplied_mail.subject}'.", next_steps=f"Sent the following email:\n\n{reply_text}", session_date=datetime.now(timezone.utc))
                    session.add(unreplied_mail)
                    session.add(new_note)
                    session.commit()
                    st.success(f"Reply sent to {selected_student.name} and archived!")
                    st.session_state.clear()
                    st.rerun()

def render_new_email_mode(model, tokenizer, device):
    """Renders the UI for sending a new, proactive email."""
    st.header("✍️ Send a New, Proactive Email")
    
    all_students = get_students()
    student_names = [s.name for s in all_students]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Student & Task Selection")
        selected_student_name = st.selectbox("1. Select a Student", student_names, index=0)
        email_goal = st.text_area("2. What is the goal of this email?", "Proactively check in on the student about their exam preparations and offer support.", height=100)
        
        selected_student = next((s for s in all_students if s.name == selected_student_name), None)
        if selected_student:
            with st.expander("View Student History & Persona", expanded=True):
                st.markdown(get_student_context(selected_student))

    with col2:
        st.subheader("🤖 AI-Generated Email Draft")
        if st.button("Generate AI Email Draft"):
            if selected_student:
                with st.spinner("Generating AI draft..."):
                    context_for_prompt = get_student_context(selected_student)
                    final_prompt = create_dynamic_prompt(context_for_prompt, email_goal)
                    ai_email = generate_text(model, tokenizer, device, final_prompt)
                    st.session_state['new_email_draft'] = ai_email

        email_text = st.text_area("Edit and finalize your email:", value=st.session_state.get('new_email_draft', ''), height=250)

        if st.button("✔️ Send Email & Log Interaction"):
            if selected_student and email_text:
                new_note = CounsellingNote(student_id=selected_student.id, session_type="Proactive Email Sent", notes=f"Sent a proactive email with the goal: '{email_goal}'.", next_steps=f"Sent the following email:\n\n{email_text}", session_date=datetime.now(timezone.utc))
                session.add(new_note)
                session.commit()
                st.success(f"Email sent to {selected_student.name} and logged in their history!")
                st.session_state.clear()


if __name__ == "__main__":
    main()