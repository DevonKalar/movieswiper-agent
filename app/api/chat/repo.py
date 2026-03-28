from pymongo import ReturnDocument
from app.extensions import mongo_db
from .schemas import ConversationDocument, ConversationRecord, MessageDocument, MessageRecord


# --- Conversation ---

def list_conversations() -> list[ConversationRecord]:
    col = mongo_db['conversations']
    docs = list(col.find().sort('_id', -1))
    for d in docs:
        d["_id"] = str(d["_id"])
    return [ConversationRecord.model_validate(d) for d in docs]


def insert_conversation(doc: ConversationDocument) -> ConversationRecord:
    col = mongo_db['conversations']
    data = doc.model_dump()
    result = col.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return ConversationRecord.model_validate(data)


def find_conversation(conversation_id: str) -> ConversationRecord | None:
    col = mongo_db['conversations']
    doc = col.find_one({"conversation_id": conversation_id})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return ConversationRecord.model_validate(doc)


def update_conversation(conversation_id: str, updates: dict) -> ConversationRecord | None:
    col = mongo_db['conversations']
    doc = col.find_one_and_update(
        {"conversation_id": conversation_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return ConversationRecord.model_validate(doc)


def delete_conversation(conversation_id: str) -> bool:
    col = mongo_db['conversations']
    result = col.delete_one({"conversation_id": conversation_id})
    return result.deleted_count > 0


# --- Messages ---

def list_chat_messages(conversation_id: str, limit: int = 50) -> list[MessageRecord]:
    col = mongo_db['chat_messages']
    cursor = (col.find({"conversation_id": conversation_id})
                 .sort('_id', -1)
                 .limit(limit))
    docs = list(cursor)
    for d in docs:
        d["_id"] = str(d["_id"])
    return [MessageRecord.model_validate(d) for d in docs]


def insert_message(doc: MessageDocument) -> MessageRecord:
    col = mongo_db['chat_messages']
    data = doc.model_dump()
    result = col.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return MessageRecord.model_validate(data)


def find_message(conversation_id: str, message_id: str) -> MessageRecord | None:
    col = mongo_db['chat_messages']
    doc = col.find_one({"conversation_id": conversation_id, "message_id": message_id})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return MessageRecord.model_validate(doc)


def delete_message(conversation_id: str, message_id: str) -> bool:
    col = mongo_db['chat_messages']
    result = col.delete_one({"conversation_id": conversation_id, "message_id": message_id})
    return result.deleted_count > 0
