import streamlit as st
from openai import OpenAI
import pandas as pd
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Warrior Knowledge Dojo",
    page_icon="🦅",
    layout="centered"
)

# --- 2. CONFIGURATION ---
# !!! PASTE YOUR FULL GOOGLE SHEET URL BELOW !!!
# Ensure the sheet is "Anyone with the link -> Viewer"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1gtz95NNWYXmyG8a0s7cwg8e9kGa5rXyXmes1Gs67KTw/edit?gid=0#gid=0" 

# --- 3. STYLING (Mobile Safe) ---
st.markdown("""
    <style>
    /* Prevent iOS Zoom on focus */
    input, textarea, select {
        font-size: 16px !important;
    }
    
    h1, h2, h3 {
        color: #1E90FF !important; 
        font-family: 'Arial', sans-serif;
    }
    
    /* Mobile-Friendly Buttons */
    div.stButton > button {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
        font-size: 18px !important; 
        height: 60px;
        width: 100%;
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

# --- 4. AUTHENTICATION ---
try:
    # We use a safer way to get secrets to prevent crashes if missing
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        client = OpenAI(api_key=api_key)
    else:
        st.error("⚠️ API Key required in Secrets.")
        st.stop()
except Exception as e:
    st.error("Authentication Error: " + str(e))
    st.stop()

# --- 5. LOAD DATA (Safe Mode) ---
@st.cache_data(ttl=600)
def load_knowledge_base(url):
    try:
        # 1. Convert "Edit" link to "Export" link
        export_url = url
        if "/edit" in url:
            if "gid=" in url:
                export_url = url.replace("/edit#gid=", "/export?format=csv&gid=")
            else:
                export_url = url.split("/edit")[0] + "/export?format=csv"

        # 2. Read directly with Pandas
        df = pd.read_csv(export_url)
        # Force conversion to string to prevent syntax errors
        return dict(zip(df.iloc[:, 0].astype(str), df.iloc[:, 1].astype(str)))
    except Exception as e:
        return None

KNOWLEDGE_BASE = load_knowledge_base(SHEET_URL)

if not KNOWLEDGE_BASE:
    st.error("⚠️ Connection Error. \n\n1. Make sure your Google Sheet is set to 'Anyone with the link' -> 'Viewer'.\n2. Paste the link in Line 16.")
    st.stop()

# --- 6. SESSION STATE ---
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

# --- 7. HEADER ---
st.title("🦅 Warrior Knowledge Dojo")
st.markdown("**Det 925 Training Assistant**")
st.divider()

target_quote_name = st.session_state.current_q
# Safety check to ensure quote exists
if target_quote_name not in KNOWLEDGE_BASE:
    new_question()
    target_quote_name = st.session_state.current_q

correct_answer = KNOWLEDGE_BASE[target_quote_name]
st.subheader(target_quote_name)

# --- 8. LOGIC LOOP ---
if not st.session_state.answer_submitted:
    with st.form(key='dojo_form'):
        user_attempt = st.text_area("Type the quote:", height=150)
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
            st.warning("SILENCE IS NOT AN ANSWER, CADET.")
        else:
            st.session_state.answer_submitted = True
            
            # --- CRITICAL: NO SPINNER (Prevents Mobile Freeze) ---
            try:
                # --- RAGE METER (Restored) ---
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

                # --- PERSONALITY ENGINE (Restored) ---
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

                # --- PROMPT CONSTRUCTION (PHONETIC MODE ENABLED) ---
                prompt = "You are a Drill Sergeant grading a Cadet.\n"
                prompt += "1. GRADING RULES (PHONETIC MODE):\n"
                prompt += "- CRITICAL: Ignore capitalization, punctuation, and spelling errors.\n"
                prompt += "- IF IT SOUNDS RIGHT: If the user's input matches the phonetic sound of the correct answer (even with sloppy typing), you MUST start with 'PASS'.\n"
                prompt += "- CATEGORY A (PASS): Input is perfect or just missing punctuation. ACTION: Say 'PASS'.\n"
                prompt += "- CATEGORY B (PASS WITH CORRECTION): Input is correct but has typos/spelling errors. ACTION: Say 'PASS'. Then gently correct the spelling. DO NOT FAIL THEM FOR TYPOS.\n"
                prompt += "- CATEGORY C (FAIL): Significant words missing or completely wrong. ACTION: Do NOT use 'PASS'. Roast them.\n\n"
                prompt += "2. STREAK CONTEXT:\n" + rage_text + "\n\n"
                prompt += "3. PERSONALITY:\n" + persona_text + "\n\n"
                prompt += "4. CONSTRAINT: Be a ONE-LINER. Short, punchy."

                # --- SAFE STRING CONSTRUCTION (Prevents Syntax Crashes) ---
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
                # This catches the crash and shows a readable error instead of code dump
                st.error("System Error: " + str(e))
                st.session_state.answer_submitted = False
            
            st.rerun()

else:
    # --- RESULT SCREEN (Restored to User Preference) ---
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
        if st.session_state.show_balloons:
            st.balloons()
    else:
        st.error(st.session_state.feedback)
        
        # Restore the Blue Info Box (Safe Formatting)
        if "PASS" not in st.session_state.feedback:
            # We use Safe Concatenation here to prevent the f-string syntax error
            msg = "**Correct Answer:**\n" + str(correct_answer)
            st.info(msg)

    if st.button("Next Question ->", type="primary", use_container_width=True):
        new_question()
        st.rerun()

# --- FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    NOTICE: This is a cadet-developed study tool unaffiliated with the Department of the Air Force.
</div>
""", unsafe_allow_html=True)

