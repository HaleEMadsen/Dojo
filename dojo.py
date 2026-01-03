import streamlit as st
from openai import OpenAI
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Warrior Knowledge Dojo",
    page_icon="🦅",
    layout="centered"
)

# --- 2. PROFESSIONAL STYLING (The "Air Force" Look) ---
# This custom CSS changes the headers to Air Force Blue and cleans up the UI.
st.markdown("""
    <style>
    /* Air Force Blue Headers */
    h1, h2, h3 {
        color: #00308F !important;
        font-family: 'Arial', sans-serif;
    }
    /* Submit Button Styling (Blue) */
    div.stButton > button:first-child {
        background-color: #00308F;
        color: white;
        border-radius: 5px;
        border: none;
    }
    /* Skip Button Styling (Grey) */
    div.stButton > button:last-child {
        color: #444;
    }
    /* Hide the default Streamlit menu for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. SECURE AUTHENTICATION ---
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    # Fallback for local testing only
    api_key = st.text_input("Enter OpenAI API Key:", type="password")
    if not api_key:
        st.warning("⚠️ API Key required to proceed.")
        st.stop()

client = OpenAI(api_key=api_key)

# --- 4. THE KNOWLEDGE BASE ---
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
    st.session_state.feedback = None # Store feedback to keep it on screen

def new_question():
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
    st.session_state.feedback = None

# --- 6. THE INTERFACE ---
st.title("🦅 Warrior Knowledge Dojo")
st.markdown("**Det 925 Training Assistant**")
st.divider()

# Display the Target
target_quote_name = st.session_state.current_q
correct_answer = KNOWLEDGE_BASE[target_quote_name]

st.subheader(f"Recite: {target_quote_name}")

# Input Box
user_attempt = st.text_area("Type the quote exactly:", height=120)

# Buttons in two columns
col1, col2 = st.columns([1, 1])

with col1:
    submit_btn = st.button("Submit", use_container_width=True)
with col2:
    skip_btn = st.button("Skip", on_click=new_question, use_container_width=True)

# --- 7. GRADING LOGIC ---
if submit_btn:
    if not user_attempt:
        st.error("SILENCE IS NOT AN ANSWER, CADET.")
    else:
        with st.spinner("Checking accuracy..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a strict Air Force Drill Sergeant. Compare the Cadet's input to the Correct Quote. If they are 100% perfect (including punctuation), say 'PASS' and be brief. If they made ANY mistake, scream at them (in text), point out exactly what word/punctuation they missed. Keep it under 3 sentences."},
                        {"role": "user", "content": f"Correct Quote: {correct_answer}\n\nCadet Input: {user_attempt}"}
                    ],
                    max_tokens=150
                )
                feedback = response.choices[0].message.content
                
                if "PASS" in feedback:
                    st.success(feedback)
                    st.balloons()
                else:
                    st.error(feedback)
                    st.info(f"**Correct Answer:**\n{correct_answer}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- 8. UPDATED FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    NOTICE: This is a cadet-developed study tool for educational use only and not an official DAF application. 
    Maintain OPSEC, and do not enter sensitive information.
</div>
""", unsafe_allow_html=True)
