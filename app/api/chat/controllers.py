from flask import jsonify, request
from .services import get_recent_messages, create_message

def get_messages():
    conversation_id = request.args["conversationId"]
    limit = int(request.args.get("limit", 50))
    return jsonify({"items": get_recent_messages(conversation_id, limit)})

def create_message():
    conversation_id = request.json["conversationId"]
    content = request.json["content"]
    role = request.json["role"]
    return jsonify({"message": create_message(conversation_id, content, role)})