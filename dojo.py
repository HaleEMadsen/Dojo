import streamlit as st
from openai import OpenAI
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Warrior Knowledge Dojo",
    page_icon="🦅",
    layout="centered"
)

# --- 2. STYLING (All Blue Buttons) ---
st.markdown("""
    <style>
    /* Vibrant Blue Headers */
    h1, h2, h3 {
        color: #1E90FF !important; 
        font-family: 'Arial', sans-serif;
    }
    
    /* ALL BUTTONS (Submit & Skip) - Electric Blue */
    div.stButton > button {
        background-color: #1E90FF;
        color: white !important;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    /* Hover Effect for ALL buttons */
    div.stButton > button:hover {
        background-color: #4da6ff; /* Lighter blue on hover */
        box-shadow: 0 0 10px rgba(30, 144, 255, 0.5);
    }

    /* Hide default menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    api_key = st.text_input("Enter OpenAI API Key:", type="password")
    if not api_key:
        st.warning("⚠️ API Key required to proceed.")
        st.stop()

client = OpenAI(api_key=api_key)

# --- 4. KNOWLEDGE BASE ---
KNOWLEDGE_BASE = {
    "Air Force Mission": "To fly, fight, and win... airpower anytime, anywhere.",
    "Space Force Mission": "Secure our Nation's interests in, from, and to space.",
    "Air Force Core Values": "Integrity First, Service Before Self, Excellence in All We Do.",
    "Code of Conduct - Article I": "I am an American, fighting in the forces which guard my country and our way of life. I am prepared to give my life in their defense.",
    "Schofield's Discipline (First Sentence)": "The discipline which makes the soldiers of a free country reliable in battle is not to be gained by harsh or tyrannical treatment.",
    "Oath of Office (First half)": "I do solemnly swear that I will support and defend the Constitution of the United States against all enemies, foreign and domestic..."
}

# --- 5. SESSION STATE ---
if 'current_q' not in st.session_state:
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
    st.session_state.feedback = ""
    st.session_state.feedback_type = "" # 'success' or 'error'

def new_question():
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
    st.session_state.feedback = ""
    st.session_state.feedback_type = ""

# --- 6. THE UI ---
st.title("🦅 Warrior Knowledge Dojo")
st.markdown("**Det 925 Training Assistant**")
st.divider()

target_quote_name = st.session_state.current_q
correct_answer = KNOWLEDGE_BASE[target_quote_name]

st.subheader(f"Recite: {target_quote_name}")

# --- FORM START ---
# Using a form enables "Ctrl+Enter" to submit and groups the buttons
with st.form(key='dojo_form'):
    user_attempt = st.text_area("Type the quote (Ctrl+Enter to Submit):", height=120)
    
    col1, col2 = st.columns(2)
    with col1:
        submit_pressed = st.form_submit_button("Submit")
    with col2:
        skip_pressed = st.form_submit_button("Skip")

# --- 7. LOGIC HANDLING ---

# Handle SKIP (Inside form, skip acts as a submit, so we check it first)
if skip_pressed:
    new_question()
    st.rerun()

# Handle SUBMIT
if submit_pressed:
    if not user_attempt:
        st.session_state.feedback = "SILENCE IS NOT AN ANSWER, CADET."
        st.session_state.feedback_type = "error"
    else:
        with st.spinner("Analyzing..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": """
                        You are a witty, constructive Air Force Drill Sergeant / UW-Madison Fan.
                        
                        GOAL: Provide feedback that sounds like a real person.
                        
                        1. IF PERFECT (phonetically):
                           - Say "PASS." 
                           - Add a short clear compliment (e.g., "Sharp.", "Good drill.", "On Target.").
                        
                        2. IF WRONG:
                           - Start with "Not quite." or "Check fire."
                           - EXPLAIN THE MISTAKE clearly and constructively (e.g., "You missed the word 'fight' between 'fly' and 'win'.").
                           - END with a mild, witty roast (UW Badger theme or AF theme).
                           
                        TONE EXAMPLES:
                        - "You forgot 'integrity'. That's literally the first one, Cadet."
                        - "You're stuttering like a Minnesota fan. The word is 'tyrannical'."
                        - "Clean it up. My grandmother recites this faster."
                        
                        Keep it under 3 sentences.
                        """},
                        {"role": "user", "content": f"Correct Quote: {correct_answer}\n\nCadet Input: {user_attempt}"}
                    ],
                    max_tokens=150
                )
                feedback_text = response.choices[0].message.content
                st.session_state.feedback = feedback_text
                
                if "PASS" in feedback_text:
                    st.session_state.feedback_type = "success"
                else:
                    st.session_state.feedback_type = "error"
                    
            except Exception as e:
                st.error(f"Error: {e}")

# --- 8. DISPLAY FEEDBACK ---
# We display feedback outside the form so it persists nicely
if st.session_state.feedback:
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
        if "PASS" in st.session_state.feedback:
            st.balloons()
    else:
        st.error(st.session_state.feedback)
        st.info(f"**Correct Answer:**\n{correct_answer}")

# --- 9. FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    NOTICE: This is a cadet-developed study tool for educational use only and not an official DAF application. 
    Maintain OPSEC, and do not enter sensitive information.
</div>
""", unsafe_allow_html=True)
