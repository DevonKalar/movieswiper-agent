from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
import uuid

# Database schemas
class Message(BaseModel):
  message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  content: str
  role: Literal["user", "assistant", "system"]
  timestamp: datetime = Field(default_factory=datetime.now)

class Conversation(BaseModel):
  title: str = Field(default="New Conversation")
  model: str = Field(default="gpt-4o")
  status: Literal["active", "archived", "deleted"] = "active"