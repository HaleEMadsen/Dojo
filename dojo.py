import streamlit as st
from openai import OpenAI
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Warrior Knowledge Dojo", page_icon="🦅")

# --- 2. SECURE AUTHENTICATION ---
# This looks for the key in Streamlit's "Secrets" vault.
# If running locally, it falls back to a manual input for testing.
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    # If no secret is found (e.g., first local run), ask for it.
    api_key = st.text_input("Enter OpenAI API Key to start:", type="password")
    if not api_key:
        st.warning("⚠️ Please enter your API Key to proceed.")
        st.stop()

client = OpenAI(api_key=api_key)

# --- 3. THE KNOWLEDGE BASE (Add your Det's specific knowledge here) ---
KNOWLEDGE_BASE = {
    "Air Force Mission": "To fly, fight, and win... airpower anytime, anywhere.",
    "Space Force Mission": "Secure our Nation's interests in, from, and to space.",
    "Air Force Core Values": "Integrity First, Service Before Self, Excellence in All We Do.",
    "Code of Conduct - Article I": "I am an American, fighting in the forces which guard my country and our way of life. I am prepared to give my life in their defense.",
    "Schofield's Discipline (First Sentence)": "The discipline which makes the soldiers of a free country reliable in battle is not to be gained by harsh or tyrannical treatment.",
    "Oath of Office (First half)": "I do solemnly swear that I will support and defend the Constitution of the United States against all enemies, foreign and domestic..."
}

# --- 4. SESSION STATE MANAGEMENT ---
if 'current_q' not in st.session_state:
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))

def new_question():
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
    st.session_state.feedback = None # Clear previous answer

# --- 5. THE UI ---
st.title("🦅 Warrior Knowledge Dojo")
st.caption("Det 925 AI Training Assistant")
st.divider()

# Display the Target
target_quote_name = st.session_state.current_q
correct_answer = KNOWLEDGE_BASE[target_quote_name]

st.subheader(f"Recite: **{target_quote_name}**")

# Input Box
user_attempt = st.text_area("Type it exactly (Watch punctuation!):", height=100)

col1, col2 = st.columns(2)
with col1:
    submit_btn = st.button("Submit to FTO", type="primary", use_container_width=True)
with col2:
    skip_btn = st.button("Skip / Next", on_click=new_question, use_container_width=True)

# --- 6. THE GRADING LOGIC ---
if submit_btn:
    if not user_attempt:
        st.error("SILENCE IS NOT AN ANSWER, CADET.")
    else:
        with st.spinner("Grading..."):
            try:
                # We use the cheaper 'gpt-4o-mini' model here
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a strict Air Force Drill Sergeant. Compare the Cadet's input to the Correct Quote. If they are 100% perfect (including punctuation), say 'PASS' and be brief. If they made ANY mistake, scream at them (in text), point out exactly what word/punctuation they missed, and tell them to drop." },
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
                    st.markdown(f"**Correct Answer:** *{correct_answer}*")
            except Exception as e:
                st.error(f"Error connecting to FTO: {e}")

# --- 7. CYA FOOTER (Critical for AFROTC Context) ---
st.divider()
st.markdown("""
<small style="color: gray;">
    DISCLAIMER: This is a cadet-developed study tool for personal use. 
    It is not an official U.S. Air Force application. 
    Do not enter PII, CUI, or OPSEC-sensitive data. 
    All knowledge checks are based on public domain information.
</small>
""", unsafe_allow_html=True)