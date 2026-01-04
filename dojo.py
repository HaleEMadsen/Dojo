import streamlit as st
from openai import OpenAI
from streamlit_gsheets import GSheetsConnection
import random
import time

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
@st.cache_data(ttl=60)
def load_knowledge_base():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        data_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        return data_dict
    except Exception as e:
        return None

kb_data = load_knowledge_base()

if not kb_data:
    st.error("⚠️ Connection Error: Check your Secrets and Google Sheet sharing settings.")
    st.stop()

KNOWLEDGE_BASE = kb_data

# --- 5. SESSION STATE INITIALIZATION ---
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

# --- 6. THE UI HEADER ---
st.title("🦅 Warrior Knowledge Dojo")
st.markdown("**Det 925 Training Assistant**")
st.divider()

if not KNOWLEDGE_BASE:
    st.error("The Knowledge Base is empty!")
    st.stop()

target_quote_name = st.session_state.current_q
if target_quote_name not in KNOWLEDGE_BASE:
    new_question()
    target_quote_name = st.session_state.current_q

correct_answer = KNOWLEDGE_BASE[target_quote_name]

st.subheader(target_quote_name)

# --- 7. MAIN LOGIC LOOP ---

# STATE A: INPUT MODE (User has NOT submitted yet)
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
            # Flip state to submitted
            st.session_state.answer_submitted = True
            
            with st.spinner("Evaluating..."):
                try:
                    # --- RAGE METER LOGIC ---
                    current_streak = st.session_state.wrong_streak
                    rage_instruction = ""
                    
                    if current_streak >= 2 and current_streak < 4:
                        rage_instruction = f"CONTEXT: The Cadet has failed {current_streak} times in a row. Start getting annoyed."
                    elif current_streak >= 4:
                        rage_instruction = f"CONTEXT: The Cadet has failed {current_streak} times in a row. BE INCANDESCENT WITH RAGE. SCREAM (use caps)."
                    
                    # --- PROBABILITY ENGINE ---
                    roll = random.uniform(0, 100)
                    
                    # Base Prompt
                    base_instruction = f"""
                    You are a Drill Sergeant grading a Cadet.
                    
                    1. GRADING RULES:
                    - **PASS**: If the words are correct, even if capitalization or punctuation is wrong. Accept minor typos. Use the word "PASS".
                    - **FAIL**: Only if words are missing or completely wrong. Do NOT use the word "PASS".
                    
                    2. STREAK CONTEXT:
                    {rage_instruction}
                    - IF THEY PASS NOW and the streak was high (4+): Acknowledge they finally stopped embarrassing themselves.
                    
                    3. CONSTRAINT:
                    Be a ONE-LINER. Short, punchy, shocking. Never explain the error.
                    """
                    
                    # Personality Logic
                    if roll < 65: 
                        persona_instruction = "Style: Standard Strict MTI, Disappointed Dad, or Bad Pun. Do NOT use slang. Do NOT mention cheese."
                    elif roll < 85: 
                        persona_instruction = """
                        Style: GEN Z BRAINROT. You MUST use modern slang.
                        Pick ONE OR TWO: skibidi, sigma, rizz, fanum tax, ohio, cap, no cap, bet, lowkey, highkey, L + ratio, goated, opps, crashout, delulu, let him cook.
                        Mix this with military discipline. It should sound unnatural.
                        """
                    elif roll < 90:
                        persona_instruction = "Style: WISCONSIN LOCAL. Briefly mention cheese curds, frozen lakes, Culver's, or Spotted Cow beer."
                    elif roll < 94:
                        persona_instruction = "Style: COMMANDER'S CHALLENGE. Reference the 'Unbroken Badger' fitness challenge as a punishment or goal."
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
                        persona_instruction = f"Style: DETACHMENT LORE. Reference: {selected_lore}"

                    # Call AI
                    final_prompt = f"{base_instruction}\n\n{persona_instruction}"
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=1.3, 
                        messages=[
                            {"role": "system", "content": final_prompt},
                            {"role": "user", "content": f"Correct Quote: {correct_answer}\n\nCadet Input: {user_attempt}"}
                        ],
                        max_tokens=100
                    )
                    
                    feedback_text = response.choices[0].message.content
                    st.session_state.feedback = feedback_text
                    
                    if "PASS" in feedback_text:
                        st.session_state.feedback_type = "success"
                        if st.session_state.wrong_streak >= 4:
                            st.session_state.show_balloons = True
                        else:
                            st.session_state.show_balloons = False
                        st.session_state.wrong_streak = 0
                    else:
                        st.session_state.feedback_type = "error"
                        st.session_state.show_balloons = False
                        st.session_state.wrong_streak += 1
                
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.answer_submitted = False
            
            # This rerun is inside the submit_pressed block
            st.rerun()

# STATE B: RESULT MODE (User has submitted)
else:
    # Display Feedback
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
        if st.session_state.show_balloons:
            st.balloons()
    else:
        st.error(st.session_state.feedback)
        if "PASS" not in st.session_state.feedback:
            st.info(f"**Correct Answer:**\n{correct_answer}")

    # Next Button
    if st.button("Next Question ->", type="primary", use_container_width=True):
        new_question()
        st.rerun()

# --- 8. FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    NOTICE: This is a cadet-developed study tool unaffiliated with the Department of the Air Force and is designed for educational purposes only. Maintain basic OPSEC.
</div>
""", unsafe_allow_html=True)
