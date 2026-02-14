from app.extensions import mongo

def list_chat_messages(conversation_id: str, limit: int = 50) -> list[dict]:
  col = mongo.db['chat_messages']
  cursor = (col.find({conversation_id: conversation_id})
                .sort('_id', -1)
                .limit(limit))
  return list(cursor)