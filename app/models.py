from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str
    sender_name: str
    text: str
    timestamp: str


class ConversationPayload(BaseModel):
    conversation_id: str
    client_name: str
    messages: List[Message]