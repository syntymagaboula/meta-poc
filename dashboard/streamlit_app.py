import streamlit as st
import requests
from collections import defaultdict

API_URL = "http://localhost:8000/messages"

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Assistant CanalBox",
    layout="wide"
)

# =========================
# OMNICHANNEL PROFESSIONAL UI STYLE - COULEURS CANALBOX GABON
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* STYLE GLOBAL ISSU DU THÈME CANALBOX */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #0b0f19 !important;
    color: #f8fafc !important;
}

.block-container {
    padding-top: 2.5rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}

/* NETTOYAGE DES CONTENEURS INTERNES DE STREAMLIT */
[data-testid="stMarkdownContainer"] > div:empty {
    display: none !important;
}
[data-testid="element-container"] {
    margin-bottom: 0px !important;
}

/* EN-TÊTE PRINCIPAL MODIFIÉ AVEC LE STYLE CANALBOX */
.workspace-header {
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.03em;
    margin-bottom: 28px;
    display: block;
    width: 100%;
    text-transform: uppercase;
}
.workspace-header span {
    color: #00ff9d;
    text-shadow: 0 0 12px rgba(0, 255, 157, 0.4);
}

/* BARRE DE CONVERSATION ACTIVE AUX COULEURS CANALBOX */
.active-chat-bar {
    background: #111827;
    padding: 16px 20px;
    border-radius: 8px;
    border-left: 4px solid #00ff9d;
    margin-bottom: 36px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    width: 100%;
}
.active-chat-title {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
}

/* CONTENEUR DE FLUX DE CHAT COMPLET */
.conversation-container {
    display: flex;
    flex-direction: column;
    width: 100%;
}

/* LIGNES DE MESSAGE AVEC ESPACEMENT VERTICAL MAXIMUM */
.msg-row {
    display: flex;
    width: 100%;
    margin-bottom: 24px; /* Grand espace pour aérer visuellement */
}
.msg-row.client-side {
    justify-content: flex-start;
}
.msg-row.agent-side {
    justify-content: flex-end;
}

/* BULLES SANS BORDURES LOURDES MAIS AVEC LES COULEURS DU PREMIER THÈME */
.msg-bubble {
    max-width: 60%;
    padding: 14px 20px; /* Plus d'espace interne pour laisser respirer le texte */
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.6;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    border: none !important; /* Suppression complète des lignes de bordure */
}

/* CLIENT (Gauche - Bleu/Gris très sombre dégradé) */
.client-side .msg-bubble {
    background: linear-gradient(135deg, #1f2937, #111827);
    color: #f3f4f6;
    border: 1px solid #374151 !important;
}

/* CONSEILLER (Droite - Vert Fluo Lumineux Canalbox) */
.agent-side .msg-bubble {
    background: linear-gradient(135deg, #00ff9d, #059669);
    color: #0b0f19;
    font-weight: 500;
}

/* LABELS ET TIMESTAMPS ÉPURÉS ADAPTÉS AUX FONDS SOMBRES */
.msg-meta-sender {
    font-size: 11.5px;
    font-weight: 600;
    margin-bottom: 6px;
    display: block;
}
.client-side .msg-meta-sender {
    color: #9ca3af;
}
.agent-side .msg-meta-sender {
    color: #0b0f19;
    opacity: 0.8;
}

.msg-meta-time {
    font-size: 10.5px;
    margin-top: 8px;
    display: block;
}
.client-side .msg-meta-time {
    color: #94a3b8;
}
.agent-side .msg-meta-time {
    color: #0b0f19;
    opacity: 0.6;
    text-align: right;
}

/* SIDEBAR RECEPTION LOOK SOMBRE CANALBOX */
[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid #1f2937;
}
[data-testid="stSidebar"] .stRadio > label {
    font-size: 12px;
    font-weight: 700;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=2)
def load_messages():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []


messages = load_messages()

if not messages:
    st.warning("Aucune conversation disponible")
    st.stop()


# =========================
# GROUP
# =========================
conversations = defaultdict(list)

for m in messages:
    cid = m.get("conversation_id")
    if cid:
        conversations[cid].append(m)


# =========================
# SORT BY msg_index ONLY
# =========================
def sort_msgs(conv):
    return sorted(conv, key=lambda x: x.get("msg_index") or 0)


# =========================
# CLIENT NAME
# =========================
def get_client_name(conv):
    conv_sorted = sort_msgs(conv)

    for m in conv_sorted:
        sender = (m.get("sender_name") or "").strip()
        if sender and sender != "Conseiller Canalbox":
            return sender

    return "Client"


# =========================
# ROLE LOGIC
# =========================
def is_agent(msg):
    sender = (msg.get("sender_name") or "").strip()
    return sender == "Conseiller Canalbox"


# =========================
# MAIN HEADER
# =========================
st.markdown('<div class="workspace-header">Canal<span>box</span> Central Hub</div>', unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================
conv_ids = list(conversations.keys())

conv_map = {
    cid: get_client_name(conversations[cid])
    for cid in conv_ids
}

selected = st.sidebar.radio(
    "Files d'attente",
    conv_ids,
    format_func=lambda x: conv_map.get(x, "Client")
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Total : {len(conv_ids)} conversations actives")


# =========================
# ACTIVE CHAT HEADER
# =========================
chat = sort_msgs(conversations[selected])

st.markdown(f"""
<div class="active-chat-bar">
    <div class="active-chat-title">Fiche de contact : {conv_map[selected]}</div>
</div>
""", unsafe_allow_html=True)


# =========================
# DISPLAY CONVERSATION
# =========================
st.markdown('<div class="conversation-container">', unsafe_allow_html=True)

for msg in chat:
    text = (msg.get("message") or "").strip()
    sender = (msg.get("sender_name") or "").strip()
    ts = msg.get("timestamp", "")

    if not text or not sender:
        continue

    if is_agent(msg):
        st.markdown(f"""
        <div class="msg-row agent-side">
            <div class="msg-bubble">
                <span class="msg-meta-sender">{sender}</span>
                <div>{text}</div>
                <span class="msg-meta-time">{ts}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row client-side">
            <div class="msg-bubble">
                <span class="msg-meta-sender">{sender}</span>
                <div>{text}</div>
                <span class="msg-meta-time">{ts}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)