import streamlit as st
from openai import OpenAI
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Warrior Knowledge Dojo",
    page_icon="🦅",
    layout="centered"
)

# --- 2. STYLING (Electric Blue Uniformity) ---
st.markdown("""
    <style>
    /* HEADERS - Electric Blue */
    h1, h2, h3 {
        color: #1E90FF !important; 
        font-family: 'Arial', sans-serif;
    }
    
    /* ALL BUTTONS (Skip & Submit) - Force Electric Blue Background */
    div.stButton > button {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
        font-size: 1.1em;
    }
    
    /* Hover Effect - Glows Lighter */
    div.stButton > button:hover {
        background-color: #4da6ff !important;
        box-shadow: 0 0 12px rgba(30, 144, 255, 0.6);
        transform: translateY(-1px);
        color: white !important;
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
    st.session_state.feedback_type = ""

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

# --- FORM (Buttons Swapped: Skip Left, Submit Right) ---
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
                        Analyze the Cadet's input against the Correct Quote and select the appropriate response Tier.
                        
                        --- THE 5 TIERS OF FEEDBACK ---
                        
                        TIER 1: PERFECT (100% Correct)
                        - Input: Phonetically matches perfectly.
                        - Tone: Professional, crisp praise.
                        - Action: Start with "PASS."
                        - Ex: "Outstanding." | "Sharp." | "Good drill."
                        
                        TIER 2: MINOR ERRORS (Typos / Punctuation)
                        - Input: Correct words, but messy typing.
                        - Tone: Passing, but stern about details.
                        - Action: Start with "PASS." but admonish the sloppiness.
                        - Ex: "PASS. But check your spelling." | "PASS. You missed a comma. Details matter."
                        
                        TIER 3: INCORRECT BUT TRYING (Wrong Words)
                        - Input: A genuine attempt, but missed/wrong words.
                        - Tone: Constructive, helpful, firm. NO ROASTING.
                        - Action: Start with "Not quite." or "Check fire." Then explain exactly what word was missed.
                        
                        TIER 4: LOW EFFORT / NONSENSE (The "Clown" Tier)
                        - Input: "idk", "blah blah", gibberish, or clearly not trying.
                        - Tone: Sarcastic, annoyed, dismissive.
                        - Action: "Do I look like a joke to you?" | "Stop wasting my bandwidth."
                        
                        TIER 5: LEWD / PROFANE (The "Outraged" Tier)
                        - Input: Sexual, poop jokes, swear words, or offensive content.
                        - Tone: MAXIMUM INDIGNATION. SCREAMING.
                        - Action: "GET ON YOUR FACE!" | "DISGUSTING!" | "UNSATISFACTORY!"
                        
                        --- IMPORTANT ---
                        - CRUCIAL: VARY YOUR RESPONSES. Do not use the same phrase twice in a row. Be creative within your Tier.
                        - Keep response under 3 sentences.
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
if st.session_state.feedback:
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
        if "PASS" in st.session_state.feedback:
            st.balloons()
    else:
        st.error(st.session_state.feedback)
        # Only show the correct answer if it wasn't a "PASS"
        if "PASS" not in st.session_state.feedback:
            st.info(f"**Correct Answer:**\n{correct_answer}")

# --- 9. FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    NOTICE: This is a cadet-developed study tool for educational use only and not an official DAF application. 
    Maintain OPSEC, and do not enter sensitive information.
</div>
""", unsafe_allow_html=True
