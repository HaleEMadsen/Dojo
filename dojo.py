import streamlit as st
from openai import OpenAI
from streamlit_gsheets import GSheetsConnection
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Warrior Knowledge Dojo",
    page_icon="🦅",
    layout="centered"
)

# --- 2. STYLING ---
st.markdown("""
    <style>
    h1, h2, h3 {
        color: #1E90FF !important; 
        font-family: 'Arial', sans-serif;
    }
    div.stButton > button {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
        font-size: 1.1em;
    }
    div.stButton > button:hover {
        background-color: #4da6ff !important;
        box-shadow: 0 0 12px rgba(30, 144, 255, 0.6);
        transform: translateY(-1px);
        color: white !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.warning("⚠️ API Key required in Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- 4. LOAD DATA FROM GOOGLE SHEETS ---
# Cache allows us to check for updates every 60 seconds
@st.cache_data(ttl=60)
def load_knowledge_base():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # ttl=0 here ensures we get fresh data from Google, not the library's internal cache
        df = conn.read(ttl=0)
        # Assumes Column 1 = Key (Topic), Column 2 = Value (Answer)
        data_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        return data_dict
    except Exception as e:
        return None

kb_data = load_knowledge_base()

if not kb_data:
    st.error("⚠️ Connection Error: Check your Secrets and Google Sheet sharing settings.")
    st.stop()

KNOWLEDGE_BASE = kb_data

# --- 5. SESSION STATE ---
if 'current_q' not in st.session_state:
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
    st.session_state.feedback = ""
    st.session_state.feedback_type = ""

def new_question():
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
    st.session_state.feedback = ""
    st.session_state.feedback_type = ""

# --- 6. THE UI ---
st.title("🦅 Warrior Knowledge Dojo")
st.markdown("**Det 925 Training Assistant**")
st.divider()

# Handle case where sheet might be empty or keys missing
if not KNOWLEDGE_BASE:
    st.error("The Knowledge Base is empty! Add rows to your Google Sheet.")
    st.stop()

target_quote_name = st.session_state.current_q
# Ensure the key exists (in case sheet changed while user was active)
if target_quote_name not in KNOWLEDGE_BASE:
    new_question()
    target_quote_name = st.session_state.current_q

correct_answer = KNOWLEDGE_BASE[target_quote_name]

st.subheader(f"Recite: {target_quote_name}")

with st.form(key='dojo_form'):
    user_attempt = st.text_area("Type the quote (Ctrl+Enter to Submit):", height=120)
    col1, col2 = st.columns(2)
    with col1:
        skip_pressed = st.form_submit_button("Skip", use_container_width=True)
    with col2:
        submit_pressed = st.form_submit_button("Submit", use_container_width=True)

# --- 7. LOGIC HANDLING ---
if skip_pressed:
    new_question()
    st.rerun()

if submit_pressed:
    if not user_attempt:
        st.session_state.feedback = "SILENCE IS NOT AN ANSWER, CADET."
        st.session_state.feedback_type = "error"
    else:
        with st.spinner("Evaluating..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": """
                        You are a strict but fair Air Force Drill Sergeant.
                        Analyze the Cadet's input against the Correct Quote.
                        
                        TIER 1: PERFECT MATCH -> PASS. (Commendable attention to detail).
                        TIER 2: TINY TYPO (Punctuation/Spelling) -> PASS. (Point it out, but accept it).
                        TIER 3: MINOR ERRORS (1-2 wrong words) -> PASS WITH WARNING. (Sloppy, but acceptable).
                        TIER 4: SIGNIFICANT ERRORS (Right idea, wrong phrasing) -> FAIL. (Go back to study).
                        TIER 5: WRONG QUOTE (Confused with another quote) -> FAIL. (Total lack of preparation).
                        TIER 6: NONSENSE/GIBBERISH -> ROAST. (Are you even trying?).
                        TIER 7: PROFANE/INSUBORDINATE -> RAGE. (Disciplinary action required).
                        
                        Keep response under 3 sentences.
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

# --- 8. FEEDBACK DISPLAY ---
if st.session_state.feedback:
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
        if "PASS" in st.session_state.feedback:
            st.balloons()
    else:
        st.error(st.session_state.feedback)
        if "PASS" not in st.session_state.feedback:
            st.info(f"**Correct Answer:**\n{correct_answer}")

# --- 9. FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    NOTICE: This is a cadet-developed study tool unaffiliated with the Department of the Air Force and is designed for educational purposes only. Maintain basic OPSEC.
</div>
""", unsafe_allow_html=True)
