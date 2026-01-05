import streamlit as st
from openai import OpenAI
from streamlit_gsheets import GSheetsConnection
import random
import time
import pandas as pd
import base64  # Needed for the invisible audio player

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
        
        # 1. Create Question -> Answer dict
        data_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        
        # 2. Create Question -> Image URL dict
        if "Image_URL" in df.columns:
            df["Image_URL"] = df["Image_URL"].fillna("")
            image_dict = dict(zip(df.iloc[:, 0], df["Image_URL"]))
        else:
            image_dict = {}
            
        return data_dict, image_dict

    except Exception as e:
        return None, None

kb_data, img_data = load_knowledge_base()

if not kb_data:
    st.error("⚠️ Connection Error: Check your Secrets and Google Sheet sharing settings.")
    st.stop()

KNOWLEDGE_BASE = kb_data
IMAGE_BASE = img_data

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

# --- AUDIO STATE INIT ---
if 'last_audio' not in st.session_state:
    st.session_state.last_audio = None

def new_question():
    st.session_state.current_q = random.choice(list(KNOWLEDGE_BASE.keys()))
    st.session_state.feedback = ""
    st.session_state.feedback_type = ""
    st.session_state.answer_submitted = False 
    st.session_state.show_balloons = False
    st.session_state.last_audio = None  # Reset audio

# --- 6. THE UI HEADER ---
st.title("🦅 Warrior Knowledge Dojo")
st.markdown("**Det 925 Training Assistant**")
st.divider()

target_quote_name = st.session_state.current_q
if target_quote_name not in KNOWLEDGE_BASE:
    new_question()
    target_quote_name = st.session_state.current_q

correct_answer = KNOWLEDGE_BASE[target_quote_name]

# --- DISPLAY QUESTION & OPTIONAL IMAGE ---
st.subheader(target_quote_name)

if target_quote_name in IMAGE_BASE:
    image_url = IMAGE_BASE[target_quote_name]
    if image_url and str(image_url).strip() != "" and str(image_url).startswith("http"):
        try:
            st.image(image_url, caption="Visual Identification Required", use_container_width=True)
        except:
            st.warning(f"Could not load image. Link might be broken: {image_url}")

# --- 7. MAIN LOGIC LOOP ---

# STATE A: INPUT MODE (User has NOT submitted yet)
if not st.session_state.answer_submitted:
    with st.form(key='dojo_form'):
        user_attempt = st.text_area("Type your answer:", height=120)
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
                    
                    if current_streak == 0:
                        rage_instruction = "CONTEXT: First attempt. Be professional."
                    elif current_streak < 3:
                        rage_instruction = f"CONTEXT: They have failed {current_streak} times. Get ANNOYED/STERN."
                    elif current_streak < 5:
                        rage_instruction = f"CONTEXT: They have failed {current_streak} times. BE VERY MAD. YELL (Caps)."
                    else:
                        rage_instruction = f"CONTEXT: They have failed {current_streak} times. GO COMPLETELY ENRAGED/VICIOUS. LOSE YOUR MIND."
                    
                    # --- PROBABILITY ENGINE ---
                    roll = random.uniform(0, 100)
                    
                    # --- SAFE PROMPT CONSTRUCTION ---
                    base_template = """
                    You are a Drill Sergeant grading a Cadet.
                    
                    1. EVALUATE THE INPUT:
                    
                    - **CATEGORY A: Correct** would be phonetically correct if read aloud.
                      ACTION: You MUST start with the word "Correct." Be brief/neutral.
                    
                    - **CATEGORY B: SLOPPY PASS (Grammar/Typos/Minor Phrasing)**
                      If the answer is technically right but has bad grammar, missing capitalization, or is slightly misphrased but clearly understands the concept.
                      ACTION: You MUST start with the word "Correct".
                      TONE: Forgiving but corrective. Do NOT use the fail-state.
                    
                    - **CATEGORY C: PROFANITY / INSUBORDINATION**
                      ACTION: FAIL. GO VICIOUS IMMEDIATELY. Ignore streak count. Destroy them verbally. Call them an absurd insult.
                    
                    - **CATEGORY D: TOTAL FAILURE**
                      Input is factually wrong.
                      ACTION: Do NOT use the word "Correct".
                      TONE: Follow the STREAK CONTEXT below.
                    
                    2. STREAK CONTEXT:
                    {rage}
                    
                    3. CONSTRAINT:
                    Responses may include up to 2 sentences. The first sentence must succinctly explain how the cadet should have found the correct answer and why their answer is wrong. The second sentence must be in **ALL CAPS**. Use multiple exclamation marks (e.g. 'MOVE IT!!!'). Use short, staccato sentences to force the voice engine to be aggressive.
                    """
                    
                    base_instruction = base_template.format(rage=rage_instruction)
                    
                    # Personality Logic
                    if roll < 75: 
                        persona_instruction = "Style: Standard MTI, Disappointed Dad, or Bad Pun. Do NOT use slang. Do NOT mention cheese. (IMPORTANT: But still respect the phonetic rule. Answers are correct if they sound right when read aloud. Do not nitpick or call it a near miss if the errors are just capitalization or grammar."
                    elif roll < 85: 
                        persona_instruction = """
                        Style: GEN Z BRAINROT. You MUST use modern slang.
                        Pick ONE OR TWO: skibidi, sigma, rizz, fanum tax, ohio, cap, no cap, bet, lowkey, highkey, L + ratio, goated, opps, crashout, fade, smooth brain, lard head, monkey, goblin, clown, goober, goon, delulu, let him cook.
                        Mix this with military discipline. It should sound unnatural.
                        """
                    elif roll < 90:
                        persona_instruction = "Style: WISCONSIN LOCAL. Briefly mention cheese curds, frozen lakes, Culver's, or Spotted Cow beer."
                    elif roll < 93:
                        persona_instruction = "Style: COMMANDER'S CHALLENGE. Reference the 'Unbroken Badger' fitness challenge as a punishment or goal."
                    else:
                        lore_options = [
                            "Ask if they are trying to flood the Det bathroom again.",
                            "Tell them this effort is weaker than the dining-in horseradish.",
                            "Tell them to fix it before they end up in the hospital at Special Warfare PT.",
                            "Tell them to focus before they rear-end someone in the Culver's drive-through.",
                            "Scream an obnoxious Area Greeting at them. e.g. Area, greet the clown who doesn't study Warrior Knowledge!",
                            "Tell them they are slower than an Old Ginger.",
                            "Tell them LLAB just got moved back to 0600 because of them.",
                            "Tell them we're bringing alligator crawls back to PT because of them.",
                            "Tell them that our Special Guest would like a word with them.",
                            "Tell them LLABs got extended back to four hours because of their incompetence."
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

                    # --- GENERATE AUDIO (ONYX VOICE + FAST SPEED) ---
                    try:
                        audio_response = client.audio.speech.create(
                            model="tts-1",
                            voice="onyx",
                            input=feedback_text,
                            speed=1.25
                        )
                        st.session_state.last_audio = audio_response.content
                    except Exception as audio_e:
                        st.warning(f"Audio generation failed: {audio_e}")
                    
                    # Logic: If the AI was forced to say "Correct" (even for sloppy answers), 
                    # we treat it as success and do NOT flash/siren.
                    if "Correct" in feedback_text:
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
            
            st.rerun()

# STATE B: RESULT MODE (User has submitted)
else:
    # --- 1. VISUAL FLASHBANG (Only on Total Failure) ---
    if st.session_state.feedback_type == "error":
        st.markdown("""
            <style>
            @keyframes flash {
                0% { background-color: #ff0000; }
                50% { background-color: #8b0000; }
                100% { background-color: #0e1117; }
            }
            .stApp {
                animation: flash 0.4s ease-in-out;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.error(st.session_state.feedback)
        if "Correct" not in st.session_state.feedback:
            st.info(f"**Correct Answer:**\n{correct_answer}")
            
    # --- 2. SUCCESS STATE (Includes Sloppy Pass) ---
    elif st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
        if st.session_state.show_balloons:
            st.balloons()

    # --- 3. AUDIO ASSAULT (Layered & Looping) ---
    if st.session_state.last_audio:
        try:
            # A. The MTI Voice (Encoded)
            b64_voice = base64.b64encode(st.session_state.last_audio).decode()
            
            # B. The Stress Background
            siren_html = ""
            if st.session_state.feedback_type == "error":
                stress_sounds = [
                    "https://upload.wikimedia.org/wikipedia/commons/5/5e/Klaxon_1.ogg", 
                    "https://upload.wikimedia.org/wikipedia/commons/3/3d/Air_raid_siren.ogg",
                    "https://upload.wikimedia.org/wikipedia/commons/f/f3/Beep_short.ogg" 
                ]
                selected_siren = random.choice(stress_sounds)
                
                # HTML5 Audio with ID for JS targeting
                siren_html = f"""
                    <audio id="siren_player" autoplay loop volume="1.0">
                        <source src="{selected_siren}" type="audio/ogg">
                        <source src="{selected_siren}" type="audio/mp3">
                    </audio>
                """

            # C. Combine them using a 0-pixel height container (NOT display:none)
            # We also add a small script to FORCE play, bypassing some browser restrictions
            md = f"""
                <div style="height:0px; overflow:hidden; opacity:0; width:0px;">
                    {siren_html}
                    <audio id="voice_player" autoplay>
                        <source src="data:audio/mp3;base64,{b64_voice}" type="audio/mp3">
                    </audio>
                </div>
                
                <script>
                    var v = document.getElementById("voice_player");
                    var s = document.getElementById("siren_player");
                    if (v) {{ v.play(); }}
                    if (s) {{ s.play(); }}
                </script>
                """
            st.markdown(md, unsafe_allow_html=True)

            # Fallback: Visible player if autoplay fails
            st.caption("Audio didn't play? Check browser permissions or use the player below:")
            st.audio(st.session_state.last_audio, format="audio/mp3")
            
        except Exception as e:
            st.warning(f"Audio playback error: {e}")

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


