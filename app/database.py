import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "messages.db"
)


# ==========================
# CONNECTION
# ==========================

def get_connection():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


# ==========================
# INIT DB
# ==========================

def init_db():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS conversations(
        conversation_id TEXT PRIMARY KEY,
        client_name TEXT,
        updated_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        sender_name TEXT,
        role TEXT,
        message TEXT,
        timestamp TEXT,
        msg_index INTEGER
    )
    """)

    conn.commit()
    conn.close()


# ==========================
# SAVE CONVERSATION
# ==========================

def save_conversation(
    conversation_id,
    client_name
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO conversations(
        conversation_id,
        client_name,
        updated_at
    )
    VALUES (?, ?, ?)
    """, (
        conversation_id,
        client_name,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


# ==========================
# UPDATE CONVERSATION
# ==========================

def update_conversation(
    conversation_id
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE conversations
    SET updated_at = ?
    WHERE conversation_id = ?
    """, (
        datetime.utcnow().isoformat(),
        conversation_id
    ))

    conn.commit()
    conn.close()


# ==========================
# CHECK DUPLICATE
# ==========================

def message_exists(
    conversation_id,
    message
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id
    FROM messages
    WHERE conversation_id = ?
    AND message = ?
    LIMIT 1
    """, (
        conversation_id,
        message
    ))

    row = cur.fetchone()

    conn.close()

    return row is not None


# ==========================
# SAVE MESSAGE
# ==========================

def save_message(
    conversation_id,
    sender_name,
    role,
    message,
    timestamp,
    msg_index=0
):

    if not message:
        return False

    if message_exists(
        conversation_id,
        message
    ):
        return False

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO messages(
            conversation_id,
            sender_name,
            role,
            message,
            timestamp,
            msg_index
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conversation_id,
            sender_name,
            role,
            message,
            timestamp,
            msg_index
        ))

        conn.commit()

        return True

    except Exception as e:

        print("ERREUR SAVE_MESSAGE:", str(e))
        return False

    finally:

        conn.close()

def get_messages(
    conversation_id
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM messages
    WHERE conversation_id = ?
    ORDER BY msg_index ASC
    """, (
        conversation_id,
    ))

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]


# ==========================
# GET ALL MESSAGES
# ==========================

def get_all_messages():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM messages
    ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]


# ==========================
# GET CONVERSATIONS
# ==========================

def get_conversations():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM conversations
    ORDER BY updated_at DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return [dict(r) for r in rows]