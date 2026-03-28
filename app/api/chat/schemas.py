from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Literal
from datetime import datetime
import uuid


# --- Request models (camelCase in → snake_case fields) ---

class CreateConversationRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: str = "New Conversation"
    model: str = "gpt-4o"


class UpdateConversationRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: str | None = None
    model: str | None = None
    status: Literal["active", "archived", "deleted"] | None = None


class CreateMessageRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    content: str
    role: Literal["user", "assistant", "system"]


# --- DB models (snake_case) ---

class ConversationDocument(BaseModel):
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Conversation"
    model: str = "gpt-4o"
    status: Literal["active", "archived", "deleted"] = "active"
    created_at: datetime = Field(default_factory=datetime.now)


class ConversationRecord(ConversationDocument):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")


class MessageDocument(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    content: str
    role: Literal["user", "assistant", "system"]
    timestamp: datetime = Field(default_factory=datetime.now)


class MessageRecord(MessageDocument):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")


# --- Response models (snake_case fields → camelCase out) ---

class ConversationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    conversation_id: str
    title: str
    model: str
    status: Literal["active", "archived", "deleted"]
    created_at: datetime


class MessageResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    message_id: str
    conversation_id: str
    content: str
    role: Literal["user", "assistant", "system"]
    timestamp: datetime
