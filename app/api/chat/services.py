from .repo import (
    list_conversations as repo_list_conversations,
    insert_conversation,
    find_conversation,
    update_conversation as repo_update_conversation,
    delete_conversation as repo_delete_conversation,
    list_chat_messages,
    insert_message,
    find_message,
    delete_message as repo_delete_message,
)
from .schemas import (
    CreateConversationRequest,
    UpdateConversationRequest,
    ConversationDocument,
    ConversationResponse,
    CreateMessageRequest,
    MessageDocument,
    MessageResponse,
)
from app.common.error_handler import NotFoundError


def _conversation_response(record) -> ConversationResponse:
    return ConversationResponse(
        conversation_id=record.conversation_id,
        title=record.title,
        model=record.model,
        status=record.status,
        created_at=record.created_at,
    )


def _message_response(record) -> MessageResponse:
    return MessageResponse(
        message_id=record.message_id,
        conversation_id=record.conversation_id,
        content=record.content,
        role=record.role,
        timestamp=record.timestamp,
    )


# --- Conversations ---

def list_conversations() -> list[ConversationResponse]:
    return [_conversation_response(r) for r in repo_list_conversations()]


def create_conversation(req: CreateConversationRequest) -> ConversationResponse:
    doc = ConversationDocument(title=req.title, model=req.model)
    record = insert_conversation(doc)
    return _conversation_response(record)


def get_conversation(conversation_id: str) -> ConversationResponse:
    record = find_conversation(conversation_id)
    if record is None:
        raise NotFoundError(f"Conversation {conversation_id} not found")
    return _conversation_response(record)


def update_conversation(conversation_id: str, req: UpdateConversationRequest) -> ConversationResponse:
    updates = req.model_dump(exclude_none=True)
    if not updates:
        return get_conversation(conversation_id)
    record = repo_update_conversation(conversation_id, updates)
    if record is None:
        raise NotFoundError(f"Conversation {conversation_id} not found")
    return _conversation_response(record)


def delete_conversation(conversation_id: str) -> None:
    found = repo_delete_conversation(conversation_id)
    if not found:
        raise NotFoundError(f"Conversation {conversation_id} not found")


# --- Messages ---

def get_recent_messages(conversation_id: str, limit: int = 50) -> list[MessageResponse]:
    records = list_chat_messages(conversation_id, limit=limit)
    return [_message_response(r) for r in records]


def create_message(conversation_id: str, req: CreateMessageRequest) -> MessageResponse:
    doc = MessageDocument(
        conversation_id=conversation_id,
        content=req.content,
        role=req.role,
    )
    record = insert_message(doc)
    return _message_response(record)


def get_message(conversation_id: str, message_id: str) -> MessageResponse:
    record = find_message(conversation_id, message_id)
    if record is None:
        raise NotFoundError(f"Message {message_id} not found")
    return _message_response(record)


def delete_message(conversation_id: str, message_id: str) -> None:
    found = repo_delete_message(conversation_id, message_id)
    if not found:
        raise NotFoundError(f"Message {message_id} not found")
