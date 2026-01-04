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

# --- 2. MOBILE-OPTIMIZED CSS ---
st.markdown("""
    <style>
    /* Prevent iOS Zoom on focus */
    input, textarea, select {
        font-size: 16px !important;
    }
    
    /* Better Header Styling */
    h1, h2, h3 {
        color: #1E90FF !important; 
        font-family: 'Arial', sans-serif;
    }
    
    /* Mobile-Friendly Buttons */
    div.stButton > button {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 8px; /* Softer corners for mobile */
        border: none;
        font-weight: bold;
        height: 55px; /* Taller for touch targets */
        font-size: 18px !important;
        width: 100%;
    }
    
    div.stButton > button:active {
        background-color: #0056b3 !important;
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

# --- 4. LOAD DATA (MOBILE FIXED) ---
@st.cache_data(ttl=600) # Cache for 10 mins to prevent Mobile Timeouts
def load_knowledge_base():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # ttl=600 prevents constant reloading which kills mobile data
        df = conn.read(ttl=600) 
        data_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        return data_dict
    except:
        return None

KNOWLEDGE_BASE = load_knowledge_base()

if not KNOWLEDGE_BASE:
    st.error("⚠️ Database Error. Reload the page.")
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
st.title("🦅 Warrior Dojo")
st.caption("Det 925 Training Assistant")
st.divider()

target_quote_name = st.session_state.current_q
if target_quote_name not in KNOWLEDGE_BASE:
    new_question()
    target_quote_name = st.session_state.current_q

correct_answer = KNOWLEDGE_BASE[target_quote_name]
st.subheader(target_quote_name)

# --- 7. LOGIC LOOP ---
if not st.session_state.answer_submitted:
    with st.form(key='dojo_form', clear_on_submit=False):
        # Height=150 makes it easier to tap on phones
        user_attempt = st.text_area("Your Answer:", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            skip_pressed = st.form_submit_button("Skip")
        with col2:
            submit_pressed = st.form_submit_button("Submit")

    if skip_pressed:
        new_question()
        st.rerun()

    if submit_pressed:
        if not user_attempt.strip():
            st.warning("Silence is not an answer, Cadet.")
        else:
            st.session_state.answer_submitted = True
            
            with st.spinner("Drill Sergeant is thinking..."):
                try:
                    # --- 1. RAGE METER (Content Preserved) ---
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

                    # --- 2. PERSONALITY ENGINE (Content Preserved) ---
                    roll = random.uniform(0, 100)
                    persona_text = ""
                    
                    if roll < 65:
                        persona_text = "Style: Strict MTI, Disappointed Dad, or Bad Pun. No slang."
                    elif roll < 85:
                        persona_text = "Style: GEN Z BRAINROT. Use: skibidi, sigma, rizz, fanum tax, no cap, bet, lowkey, L + ratio, goated, opps, crashout, delulu, let him cook."
                    elif roll < 90:
                        persona_text = "Style: WISCONSIN LOCAL. Mention cheese curds, frozen lakes, Culver's, or Spotted Cow."
                    elif roll < 94:
                        persona_text = "Style: COMMANDER'S CHALLENGE. Threaten them with the 'Unbroken Badger' workout."
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
                        persona_text = "Style: DETACHMENT LORE. Reference: " + selected_lore

                    # --- 3. PROMPT CONSTRUCTION ---
                    prompt = "You are a Drill Sergeant grading a Cadet.\n"
                    prompt += "1. EVALUATE THE INPUT:\n"
                    prompt += "- CATEGORY A (PASS): Input is correct. Ignore caps/punctuation/typos. ACTION: You MUST use the word 'PASS'. Be brief.\n"
                    prompt += "- CATEGORY B (NEAR MISS): Input is 80% correct but sloppy. ACTION: Do NOT use 'PASS'. TONE: Stern/Corrective. 'Tighten it up'. DO NOT ROAST YET (unless streak is high).\n"
                    prompt += "- CATEGORY C (PROFANITY/INSUBORDINATION): Input has swear words/backtalk. ACTION: FAIL. GO VICIOUS IMMEDIATELY. Ignore streak count. Destroy them.\n"
                    prompt += "- CATEGORY D (TOTAL FAILURE): Input is wrong. ACTION: Do NOT use 'PASS'. TONE: Roast them.\n\n"
                    prompt += "2. STREAK CONTEXT:\n" + rage_text + "\n\n"
                    prompt += "3. PERSONALITY:\n" + persona_text + "\n\n"
                    prompt += "4. CONSTRAINT: Be a ONE-LINER. Short, punchy."

                    # Safe String Construction for Mobile Stability
                    user_content_str = "Correct Quote: " + str(correct_answer) + "\n\nCadet Input: " + str(user_attempt)

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
    # RESULT SCREEN
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
        if st.session_state.show_balloons:
            st.balloons()
    else:
        st.error(st.session_state.feedback)
        if "PASS" not in st.session_state.feedback:
            # Uses markdown for better wrapping on small screens
            st.markdown(f"**Correct Answer:**\n\n_{correct_answer}_")

    if st.button("Next Question ->", type="primary"):
        new_question()
        st.rerun()

# --- FOOTER ---
st.divider()
st.caption("Cadet-developed study tool. Unaffiliated with the USAF.")
