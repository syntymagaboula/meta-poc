from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import re
import json
from datetime import datetime

from database import (
    init_db,
    save_conversation,
    save_message,
    get_messages,
    get_all_messages,
    update_conversation
)

app = FastAPI()

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ======================
# CLEANING
# ======================

UI_PATTERNS = [
    "associez un profil instagram",
    "en savoir plus",
    "liker",
    "facebook",
    "instagram",
    "boîte de réception",
]

def clean_message(text: str):

    if not text:
        return ""

    text = text.replace("\xa0", " ")

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    lower = text.lower()

    for pattern in UI_PATTERNS:
        if pattern in lower:
            return ""

    text = re.sub(
        r"Aujourd’hui\s*\d{1,2}:\d{2}",
        "",
        text
    )

    return text.strip()


# ======================
# ROLE DETECTION
# ======================

AGENT_PATTERNS = [
    "bonjour, je suis",
    "je prends en charge",
    "nous allons vous assister",
    "pour vous apporter mon assistance",
    "je vous prie de patienter",
    "veuillez me communiquer",
    "nous sommes en attente",
    "toujours en attente",
    "canalbox vous présente",
    "merci de nous confirmer",
    "un instant s'il vous plaît",
    "un instant s'il vous plait",
    "je comprends",
    "je vous remercie",
    "nous vous souhaitons la bienvenue",
    "êtes-vous toujours connecté",
    "êtes-vous actuellement à votre domicile",
    "votre demande a été relancée",
    "votre plainte",
    "nous sommes en promotion",
    "nous vous proposons",
    "nous vous invitons"
]

def infer_role(message: str):

    lower = message.lower()

    for pattern in AGENT_PATTERNS:
        if pattern in lower:
            return "agent"

    return "client"


# ======================
# THREAD ID
# ======================

def extract_thread_id(payload):

    return (
        payload.get("conversation_id")
        or hashlib.md5(
            str(payload).encode()
        ).hexdigest()
    )


def parse_timestamp(value):

    if not value:
        return datetime.utcnow().isoformat()

    try:
        return datetime.strptime(
            value,
            "%d/%m/%Y %H:%M"
        ).isoformat()
    except Exception:
        return datetime.utcnow().isoformat()
# ======================
# NORMALIZATION
# ======================

def normalize(
    msg,
    conversation_id,
    fallback_name
):

    raw = (
        msg.get("text")
        or msg.get("message")
        or ""
    )

    clean = clean_message(raw)

    if not clean:
        return None

    role = infer_role(clean)

    return {
        "conversation_id": conversation_id,

        "sender_name":
            msg.get("sender_name")
            or fallback_name
            or "Client Facebook",

        "role": role,

        "message": clean,

        "timestamp":
            parse_timestamp(
                msg.get("timestamp")
            ),
        "msg_index":
            msg.get("index", 0)
    }


# ======================
# WEBHOOK
# ======================

@app.post("/webhook/facebook")
async def webhook(request: Request):

    try:

        body = await request.body()

        print("\n====================")
        print("BODY RECU")
        print("====================")
        print(body)
        print("====================\n")

        if not body:
            return {
                "status": "error",
                "message": "body vide"
            }

        payload = json.loads(body)

        print("\n===== DEBUG =====")
        print(payload)
        print(type(payload))
        print("=================\n")

    except Exception as e:

        print("ERREUR JSON:", str(e))

        return {
            "status": "error",
            "message": str(e)
        }

    conversation_id = extract_thread_id(payload)

    # Cas extension Chrome : un seul message reçu
    if "messages" not in payload:

        messages = [{
            "message": payload.get("message", ""),
            "timestamp": payload.get("timestamp"),
            "sender_name": payload.get(
                "sender_name",
                "Client Facebook"
            )
        }]

    else:

        messages = payload.get(
            "messages",
            []
        )

    print("\n===== MESSAGES RECUS =====")

    for i, msg in enumerate(messages):
        print(
            i,
            "| sender:",
            msg.get("sender_name"),
            "| role:",
            msg.get("role"),
            "| text:",
            (msg.get("text") or msg.get("message") or "")[:120]
        )
    print(
            parse_timestamp(msg.get("timestamp"))
        )
    print("==========================\n")

    fallback = (
        payload.get("client_name")
        or payload.get("sender_name")
        or "Client Facebook"
    )

    print("CONVERSATION:", conversation_id)
    print("NB MESSAGES:", len(messages))

    save_conversation(
        conversation_id,
        fallback
    )

    saved = 0
    seen = set()

    for msg in messages:

        norm = normalize(
            msg,
            conversation_id,
            fallback
        )

        if not norm:
            continue

        key = hashlib.md5(
            (
                norm["message"]
                + str(norm["timestamp"])
            ).encode()
        ).hexdigest()

        if key in seen:
            continue

        seen.add(key)

        save_message(**norm)

        saved += 1

    update_conversation(
        conversation_id
    )

    print("MESSAGES SAUVES:", saved)

    return {
        "status": "ok",
        "conversation_id": conversation_id,
        "saved": saved
    }


# ======================
# HEALTHCHECK
# ======================

@app.get("/")
def root():

    return {
        "status": "ok"
    }


# ======================
# ALL MESSAGES
# ======================

@app.get("/messages")
def all_messages():

    rows = get_all_messages()

    return [
        {
            "conversation_id":
                r["conversation_id"],

            "sender_name":
                r["sender_name"],

            "role":
                r["role"],

            "message":
                r["message"],

            "timestamp":
                r["timestamp"]
        }
        for r in rows
    ]


# ======================
# ONE CONVERSATION
# ======================

@app.get("/messages/{conversation_id}")
def messages(
    conversation_id: str
):

    rows = get_messages(
        conversation_id
    )

    return rows