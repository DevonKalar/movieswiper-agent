from .repo import list_messages
from .schemas import Message
from typing import Literal

def get_recent_messages(conversation_id: str, limit: int):
    msgs = list_messages(conversation_id, limit=limit)
    # normalize / map ObjectId to string etc.
    for m in msgs:
        m["_id"] = str(m["_id"])
    return msgs

def create_message(conversation_id: str, content: str, role: Literal["user", "assistant", "system"]):
    message = Message(conversation_id=conversation_id, content=content, role=role)
    message.save()
    return message