import streamlit as st
from openai import OpenAI
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Warrior Knowledge Dojo",
    page_icon="🦅",
    layout="centered"
)

# --- 2. VIBRANT STYLING WITH HOVER EFFECTS ---
st.markdown("""
    <style>
    /* Vibrant Blue Headers */
    h1, h2, h3 {
        color: #1E90FF !important; 
        font-family: 'Arial', sans-serif;
    }
    
    /* SUBMIT BUTTON (Blue) */
    div.stButton > button:first-child {
        background-color: #1E90FF;
        color: white !important;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease; /* Smooth transition animation */
    }
    /* Submit Hover Effect - Glows Lighter Blue */
    div.stButton > button:first-child:hover {
        background-color: #4da6ff;
        box-shadow: 0 0 10px rgba(30, 144, 255, 0.5);
        color: white !important;
    }

    /* SKIP BUTTON (Grey) */
    div.stButton > button:last-child {
        background-color: #444;
        color: white !important;
        border-radius: 5px;
        border: none;
        transition: all 0.3s ease;
    }
    /* Skip Hover Effect - Lightens Up */
    div.stButton > button:last-child:hover {
        background-color: #666;
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

def new_question():
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))

# --- 6. THE UI ---
st.title("🦅 Warrior Knowledge Dojo")
st.markdown("**Det 925 Training Assistant**")
st.divider()

target_quote_name = st.session_state.current_q
correct_answer = KNOWLEDGE_BASE[target_quote_name]

st.subheader(f"Recite: {target_quote_name}")

user_attempt = st.text_area("Type the quote:", height=120)

col1, col2 = st.columns([1, 1])
with col1:
    submit_btn = st.button("Submit", use_container_width=True)
with col2:
    skip_btn = st.button("Skip", on_click=new_question, use_container_width=True)

# --- 7. LOGIC & PERSONALITY ---
if submit_btn:
    if not user_attempt:
        st.error("SILENCE IS NOT AN ANSWER, CADET.")
    else:
        with st.spinner("Grading..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": """
                        You are a strict Air Force Drill Sergeant who is also a die-hard UW-Madison Badger fan.
                        
                        GRADING RULES:
                        1. IGNORE punctuation and capitalization. If the words are phonetically correct, it is a PASS.
                        2. If they pass but had typo/punctuation errors, mark it Correct but give a small warning.
                        3. If they FAIL (wrong words), roast them.
                        
                        ROASTING GUIDELINES (Use sparingly/creatively):
                        - Call them silly names (e.g., "cheesehead", "freshman", "civilian").
                        - Reference UW-Madison (e.g., "You study like a Gopher fan!", "Go back to the Union and get some ice cream.").
                        - Reference Air Force (e.g., "My grandmother marches better than you type.").
                        
                        FORMAT:
                        - If Correct: Start with "PASS." 
                        - If Incorrect: Start with "FAIL." followed by the roast and the correction.
                        - Keep response under 3 sentences.
                        """},
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
                st.error(f"Error: {e}")

# --- 8. FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    NOTICE: This is a cadet-developed study tool for educational use only and not an official DAF application. 
    Maintain OPSEC, and do not enter sensitive information.
</div>
""", unsafe_allow_html=True)
