import streamlit as st
import openai
import json
import os
from gtts import gTTS
import base64
import re

# --- 1. CONFIGURATION ET SIGNATURE VISUELLE ---
st.set_page_config(
    page_title="ORACLE", 
    page_icon="✨", # Ton Favicon de luxe
    layout="wide", 
    initial_sidebar_state="expanded"
)

def save_data(data):
    """Grave les souvenirs dans le fichier JSON."""
    with open("history.json", "w") as f:
        json.dump(data, f)

def load_data():
    """Charge la mémoire persistante."""
    if os.path.exists("history.json"):
        try:
            with open("history.json", "r") as f:
                return json.load(f)
        except: pass
    return {"audace": 50, "clarte": 50, "autorite": 50, "messages": []}

# --- 2. SYNCHRONISATION MÉMOIRE ---
if 'initialized' not in st.session_state:
    user_data = load_data()
    st.session_state.messages = user_data.get("messages", [])
    st.session_state.audace = user_data.get("audace", 50)
    st.session_state.clarte = user_data.get("clarte", 50)
    st.session_state.autorite = user_data.get("autorite", 50)
    st.session_state.initialized = True

# --- 3. LOGIQUE DES COULEURS DYNAMIQUES ---
def get_status_color(v):
    if v < 40: # ROUGE
        return "linear-gradient(90deg, #FF4B4B 0%, #FF7575 100%)", "rgba(255, 75, 75, 0.6)"
    elif v < 75: # ORANGE
        return "linear-gradient(90deg, #FFA500 0%, #FFCC00 100%)", "rgba(255, 165, 0, 0.5)"
    else: # VERT
        return "linear-gradient(90deg, #00FF87 0%, #60EFFF 100%)", "rgba(0, 255, 135, 0.8)"

a_col, a_glow = get_status_color(st.session_state.audace)
c_col, c_glow = get_status_color(st.session_state.clarte)
au_col, au_glow = get_status_color(st.session_state.autorite)

# --- 4. CSS "OR NOIR" (ZÉRO BLANC & ZÉRO DEPLOY) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    /* SUPPRESSION DU BOUTON DEPLOY ET DES MENUS */
    [data-testid="stAppDeployButton"], footer, #MainMenu {{ display: none !important; }}
    
    /* INTERFACE NOIR ABSOLU */
    .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #050505 !important; border-right: 1px solid #1A1A1A !important; }}
    header {{ background-color: rgba(0,0,0,0) !important; }}

    .main-title {{ font-family: 'Cinzel', serif; font-size: 3.5rem; text-align: center; letter-spacing: 0.6em; margin-top: -60px; color: #C5A059; }}

    /* MESSAGES ÉDITORIAUX */
    .oracle-msg {{ align-self: flex-start; max-width: 85%; font-family: 'Cinzel', serif; border-left: 2px solid #C5A059; padding-left: 25px; margin-bottom: 3rem; line-height: 1.9; color: #FFFFFF; }}
    .user-msg {{ align-self: flex-end; max-width: 75%; font-family: 'Inter', sans-serif; text-align: right; border-right: 1px solid #444; padding-right: 25px; margin-bottom: 3rem; color: #DEDEDE; }}

    /* FORCE LE NOIR SUR LA BARRE DE SAISIE */
    [data-testid="stBottomBlockContainer"] {{ background-color: #000000 !important; }}
    .stChatInputContainer {{ background-color: #000000 !important; border: none !important; }}
    
    div[data-testid="stChatInput"] {{
        background-color: #000000 !important;
        border: 2px solid #C5A059 !important;
        border-radius: 12px !important;
    }}
    div[data-testid="stChatInput"] textarea {{ color: #FFFFFF !important; background-color: #000000 !important; caret-color: #C5A059 !important; }}

    /* BARRES DE PROGRESSION DYNAMIQUES */
    div[data-testid="stSidebar"] .stProgress:nth-of-type(1) div > div > div > div {{ background-image: {a_col} !important; box-shadow: 0 0 15px {a_glow}; }}
    div[data-testid="stSidebar"] .stProgress:nth-of-type(2) div > div > div > div {{ background-image: {c_col} !important; box-shadow: 0 0 15px {c_glow}; }}
    div[data-testid="stSidebar"] .stProgress:nth-of-type(3) div > div > div > div {{ background-image: {au_col} !important; box-shadow: 0 0 15px {au_glow}; }}

    .stProgress {{ height: 12px !important; margin-bottom: 25px; }}
    .score-display {{ font-family: 'Inter', sans-serif; font-size: 3.5rem; font-weight: 600; text-align: center; margin-top: 1.5rem; color: #C5A059; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. CONNEXION SÉCURISÉE (VIA SECRETS) ---
try:
    client = openai.OpenAI(
        api_key=st.secrets["GROQ_API_KEY"], 
        base_url="https://api.groq.com/openai/v1"
    )
except Exception:
    st.error("Erreur : Fichier secrets.toml manquant ou mal configuré.")
    st.stop()

def speak(text):
    """Génération vocale de l'Oracle."""
    try:
        tts = gTTS(text=text[:300], lang='fr')
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay></audio>', unsafe_allow_html=True)
    except: pass

# --- 6. SIDEBAR (CONTRÔLE DES %) ---
with st.sidebar:
    st.markdown("<div style='text-align:center; font-family:Cinzel; color:#C5A059; letter-spacing:5px;'>ORACLE</div>", unsafe_allow_html=True)
    v_on = st.toggle("VOIX ACTIVE", value=True)
    st.write("---")
    st.write("AUDACE")
    st.progress(st.session_state.audace / 100)
    st.write("CLARTÉ")
    st.progress(st.session_state.clarte / 100)
    st.write("AUTORITÉ")
    st.progress(st.session_state.autorite / 100)
    
    total = int((st.session_state.audace * 0.4) + (st.session_state.clarte * 0.3) + (st.session_state.autorite * 0.3))
    st.markdown(f'<div class="score-display">{total}%</div>', unsafe_allow_html=True)
    
    if st.button("RESET"):
        if os.path.exists("history.json"): os.remove("history.json")
        st.session_state.clear()
        st.rerun()

# --- 7. CHAT PRINCIPAL ---
st.markdown('<div class="main-title">ORACLE</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] != "system":
        cl = "user-msg" if msg["role"] == "user" else "oracle-msg"
        st.markdown(f'<div class="{cl}">{msg["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Exprimez votre intention..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Analyse..."):
        # Réponse IA
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role": "system", "content": "Tu es ORACLE. Intelligence souveraine. Ton ton est prestigieux."}] + st.session_state.messages
        )
        answer = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": answer})
        if v_on: speak(answer)

        # Évaluation cohérente (Regex)
        eval_res = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": f"Note l'intention : '{prompt}'. Réponds UNIQUEMENT: a,c,au"}]
        )
        try:
            nums = re.findall(r'\d+', eval_res.choices[0].message.content)
            if len(nums) >= 3:
                st.session_state.audace, st.session_state.clarte, st.session_state.autorite = int(nums[0]), int(nums[1]), int(nums[2])
                # SAUVEGARDE
                save_data({
                    "audace": st.session_state.audace, 
                    "clarte": st.session_state.clarte, 
                    "autorite": st.session_state.autorite, 
                    "messages": st.session_state.messages
                })
        except: pass
    st.rerun()