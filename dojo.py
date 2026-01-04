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

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    /* 1. FORCE ELECTRIC BLUE HEADERS */
    h1, h2, h3 {
        color: #1E90FF !important; 
        font-family: 'Arial', sans-serif;
    }
    
    /* 2. FORCE TEXT AREA FONT SIZE */
    .stTextArea textarea {
        font-size: 16px !important;
    }
    
    /* 3. BUTTON STYLING (Global Electric Blue) */
    /* This targets ALL buttons in the app */
    div.stButton > button {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        height: 50px;
        font-size: 18px;
    }
    div.stButton > button:hover {
        background-color: #104E8B !important;
        color: white !important;
    }
    
    /* Remove default focus borders that might look weird */
    div.stButton > button:focus {
        box-shadow: none !important;
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
@st.cache_data(ttl=600)
def load_knowledge_base():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
    except Exception as e:
        return None

KNOWLEDGE_BASE = load_knowledge_base()

if not KNOWLEDGE_BASE:
    st.error("⚠️ Database Error. Check .streamlit/secrets.toml")
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
        user_attempt = st.text_area("Your Answer:", height=150)
        
        col1, col2 = st.columns(2)
        
        # SKIP on Left, SUBMIT on Right
        with col1:
            skip_pressed = st.form_submit_button("Skip", use_container_width=True)
        with col2:
            submit_pressed = st.form_submit_button("Submit", use_container_width=True)

    if skip_pressed:
        new_question()
        st.rerun()

    if submit_pressed:
        if not user_attempt.strip():
            st.warning("Silence is not an answer, Cadet.")
        else:
            st.session_state.answer_submitted = True
            
            with st.spinner("Drill Sergeant is grading you..."):
                try:
                    # --- RAGE & LORE ---
                    streak = st.session_state.wrong_streak
                    rage_text = ""
                    if streak == 0:
                        rage_text = "Context: First attempt. Be professional."
                    elif streak < 3:
                        rage_text = "Context: Failed " + str(streak) + " times. Get ANNOYED/STERN."
                    elif streak < 5:
                        rage_text = "Context: Failed " + str(streak) + " times. BE VERY MAD. YELL (Caps)."
                    else:
                        rage_text = "Context: Failed " + str(streak) + " times. GO COMPLETELY ENRAGED/VICIOUS. LOSE YOUR MIND."

                    # --- PERSONALITY ---
                    roll = random.uniform(0, 100)
                    persona_text = ""
                    if roll < 65:
                        persona_text = "Style: Strict MTI. No slang."
                    elif roll < 85:
                        persona_text = "Style: GEN Z BRAINROT. Use: skibidi, sigma, rizz, fanum tax, no cap, goated, big back, Ohio, GOATED, bet, L, drip, fam, fade, sus, TFW, smooth brain, goon, monkey, clown."
                    elif roll < 90:
                        persona_text = "Style: WISCONSIN LOCAL. Mention cheese curds, frozen lakes, Culver's."
                    elif roll < 94:
                        persona_text = "Style: COMMANDER'S CHALLENGE. Threaten 'Unbroken Badger' which has lots of pull-ups and kettlebell work."
                    else:
                        lore_options = [
                            "Ask if they are trying to flood the Det bathroom again.",
                            "Tell them this effort is weaker than the dining-in horseradish.",
                            "Scream an obnoxious Area Greeting at them. e.g. Area, greet the dweeb who doesn't study Warrior Knowledge!",
                            "Tell them they are slower than an Old Ginger.",
                            "Tell them their nonsense is more hazardous than a Culver's drive-through."
                        ]
                        persona_text = "Style: DETACHMENT LORE. Reference: " + random.choice(lore_options)

                    # --- GRADING PROMPT ---
                    prompt = "You are a Drill Sergeant grading a Cadet.\n"
                    prompt += "1. GRADING RULES (PHONETIC MODE):\n"
                    prompt += "- CRITICAL: Ignore capitalization, punctuation, and spelling errors.\n"
                    prompt += "- IF IT SOUNDS RIGHT: If the user's input matches the phonetic sound of the correct answer, you MUST start with 'PASS'.\n"
                    prompt += "- CATEGORY A (PASS): Input is perfect or just missing punctuation. ACTION: Say 'PASS'.\n"
                    prompt += "- CATEGORY B (PASS WITH CORRECTION): Input is correct but has typos. ACTION: Say 'PASS'. Then gently correct spelling.\n"
                    prompt += "- CATEGORY C (PROFANITY): If input contains profanity, YOU MUST CALL IT OUT ('Do you kiss your mother with that mouth?!'). ESCALATE ANGER TO MAXIMUM. FAIL THEM.\n"
                    prompt += "- CATEGORY D (FAIL): Significant words missing or completely wrong. ACTION: Do NOT use 'PASS'. Roast them.\n\n"
                    prompt += "2. STREAK CONTEXT:\n" + rage_text + "\n\n"
                    prompt += "3. PERSONALITY:\n" + persona_text + "\n\n"
                    prompt += "4. CONSTRAINT: Be a ONE-LINER. Short, punchy."

                    user_content_str = f"Correct Quote: {correct_answer}\n\nCadet Input: {user_attempt}"

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=1.3, 
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": user_content_str}
                        ],
                        max_tokens=150
                    )
                    
                    feedback_text = response.choices[0].message.content
                    st.session_state.feedback = feedback_text
                    
                    if "PASS" in feedback_text:
                        st.session_state.feedback_type = "success"
                        if st.session_state.wrong_streak >= 4:
                            st.session_state.show_balloons = True
                        st.session_state.wrong_streak = 0
                    else:
                        st.session_state.feedback_type = "error"
                        st.session_state.show_balloons = False
                        st.session_state.wrong_streak += 1
                
                except Exception as e:
                    st.error(f"System Error: {e}")
                    st.session_state.answer_submitted = False
            
            st.rerun()

else:
    # --- RESULT SCREEN ---
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
        if st.session_state.show_balloons:
            st.balloons()
    else:
        st.error(st.session_state.feedback)
        if "PASS" not in st.session_state.feedback:
            st.info(f"**Correct Answer:**\n\n_{correct_answer}_")

    # --- NEXT BUTTON (Standard Button, CSS handles Color) ---
    if st.button("Next Question ->", use_container_width=True):
        new_question()
        st.rerun()

# --- FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    NOTICE: This is a cadet-developed study tool unaffiliated with the Department of the Air Force.
</div>
""", unsafe_allow_html=True)
