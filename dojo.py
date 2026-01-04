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
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("⚠️ API Key required in Secrets.")
    st.stop()

# --- 4. LOAD DATA ---
@st.cache_data(ttl=60)
def load_knowledge_base():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        data_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        return data_dict
    except:
        return None

KNOWLEDGE_BASE = load_knowledge_base()

if not KNOWLEDGE_BASE:
    st.error("⚠️ Connection Error: Check your Secrets and Google Sheet sharing settings.")
    st.stop()

# --- 5. SESSION STATE ---
if 'current_q' not in st.session_state:
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if 'wrong_streak' not in st.session_state:
    st.session_state.wrong_streak = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'feedback_type' not in st.session_state:
    st.session_state.feedback_type = ""
if 'show_balloons' not in st.session_state:
    st.session_state.show_balloons = False

def new_question():
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
    st.session_state.feedback = ""
    st.session_state.feedback_type = ""
    st.session_state.answer_submitted = False 
    st.session_state.show_balloons = False

# --- 6. HEADER ---
st.title("🦅 Warrior Knowledge Dojo")
st.markdown("**Det 925 Training Assistant**")
st.divider()

target_quote_name = st.session_state.current_q
if target_quote_name not in KNOWLEDGE_BASE:
    new_question()
    target_quote_name = st.session_state.current_q

correct_answer = KNOWLEDGE_BASE[target_quote_name]
st.subheader(target_quote_name)

# --- 7. LOGIC LOOP ---
if not st.session_state.answer_submitted:
    with st.form(key='dojo_form'):
        user_attempt = st.text_area("Type the quote (Ctrl+Enter to Submit):", height=120)
        col1, col2 = st.columns(2)
        with col1:
            skip_pressed = st.form_submit_button("Skip", use_container_width=True)
        with col2:
            submit_pressed = st.form_submit_button("Submit", use_container_width=True)

    if skip_pressed:
        new_question()
        st.rerun()

    if submit_pressed:
        if not user_attempt:
            st.error("SILENCE IS NOT AN ANSWER, CADET.")
        else:
            st.session_state.answer_submitted = True
            
            with st.spinner("Evaluating..."):
                try:
                    # --- 1. RAGE METER (Fully Restored) ---
                    streak = st.session_state.wrong_streak
                    rage_text = ""
                    if streak == 0:
                        rage_text = "Context: First attempt. Be professional."
                    elif streak < 3:
                        rage_text = f"Context: Failed {streak} times. Get ANNOYED/STERN."
                    elif streak < 5:
                        rage_text = f"Context: Failed {streak} times. BE VERY MAD. YELL (Caps)."
                    else:
                        rage_text = f"Context: Failed {streak} times. GO COMPLETELY ENRAGED/VICIOUS. LOSE YOUR MIND."

                    # --- 2. PERSONALITY ENGINE (Fully Restored) ---
                    roll = random.uniform(0, 100)
                    persona_text = ""
                    
                    if roll < 65:
                        persona_text = "Style: Strict MTI, Disappointed Dad, or Bad Pun. No slang."
                    elif roll < 85:
                        persona_text = "Style: GEN Z BRAINROT. Use: skibidi, sigma, rizz, fanum tax, no cap, bet, lowkey, L + ratio, goated, opps, crashout, delulu, let him cook."
                    elif roll < 90:
                        persona_text = "Style: WISCONSIN LOCAL. Mention cheese curds, frozen lakes, Culver's, Badgers, Ohio State, Minnesota Golfers, or Spotted Cow."
                    elif roll < 94:
                        persona_text = "Style: COMMANDER'S CHALLENGE. Threaten them with the 'Unbroken Badger."
                    else:
                        lore_options = [
                            "Ask if they are trying to flood the Det bathroom again.",
                            "Tell them this effort is weaker than the dining-in horseradish.",
                            "Tell them to fix it before they end up in the hospital at Special Warfare PT.",
                            "Tell them to focus before they rear-end someone in the Culver's drive-through.",
                            "Scream an obnoxious Area Greeting at them.",
                            "Tell them they are moving slower than the Old Ginger."
                        ]
                        selected_lore = random.choice(lore_options)
                        persona_text = f"Style: DETACHMENT LORE. Reference: {selected_lore}"

                    # --- 3. PROMPT CONSTRUCTION (Safe Concatenation Method) ---
                    # We rebuild the complex prompt line-by-line to avoid syntax errors
                    prompt = "You are a Drill Sergeant grading a Cadet.\n"
                    
                    prompt += "1. EVALUATE THE INPUT:\n"
                    prompt += "- CATEGORY A (PASS): Input is correct. Ignore caps/punctuation/typos. ACTION: You MUST use the word 'PASS'. Be brief.\n"
                    prompt += "- CATEGORY B (NEAR MISS): Input is 80% correct but sloppy. ACTION: Do
