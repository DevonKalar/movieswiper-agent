from flask import Blueprint, jsonify, request
from .services import (
    list_conversations as list_conversations_service,
    create_conversation as create_conversation_service,
    get_conversation as get_conversation_service,
    update_conversation as update_conversation_service,
    delete_conversation as delete_conversation_service,
    get_recent_messages,
    create_message as create_message_service,
    get_message as get_message_service,
    delete_message as delete_message_service,
)
from .schemas import CreateConversationRequest, UpdateConversationRequest, CreateMessageRequest
from app.common.error_handler import ValidationError

bp = Blueprint('chat', __name__)


# --- Conversations ---

@bp.get('/conversations')
def list_conversations():
    results = list_conversations_service()
    return jsonify({"items": [r.model_dump(by_alias=True, mode='json') for r in results]})


@bp.post('/conversations')
def create_conversation():
    body = request.get_json(silent=True) or {}
    req = CreateConversationRequest.model_validate(body)
    result = create_conversation_service(req)
    return jsonify({"conversation": result.model_dump(by_alias=True, mode='json')}), 201


@bp.get('/conversations/<conversation_id>')
def get_conversation(conversation_id: str):
    result = get_conversation_service(conversation_id)
    return jsonify({"conversation": result.model_dump(by_alias=True, mode='json')})


@bp.put('/conversations/<conversation_id>')
def update_conversation(conversation_id: str):
    body = request.get_json(silent=True) or {}
    req = UpdateConversationRequest.model_validate(body)
    result = update_conversation_service(conversation_id, req)
    return jsonify({"conversation": result.model_dump(by_alias=True, mode='json')})


@bp.delete('/conversations/<conversation_id>')
def delete_conversation(conversation_id: str):
    delete_conversation_service(conversation_id)
    return '', 204


# --- Messages ---

@bp.get('/conversations/<conversation_id>/messages')
def get_messages(conversation_id: str):
    limit = int(request.args.get("limit", 50))
    results = get_recent_messages(conversation_id, limit=limit)
    return jsonify({"items": [r.model_dump(by_alias=True, mode='json') for r in results]})


@bp.post('/conversations/<conversation_id>/messages')
def create_message(conversation_id: str):
    body = request.get_json(silent=True) or {}
    if not body.get("content") or not body.get("role"):
        raise ValidationError("content and role are required")
    req = CreateMessageRequest.model_validate(body)
    result = create_message_service(conversation_id, req)
    return jsonify({"message": result.model_dump(by_alias=True, mode='json')}), 201


@bp.get('/conversations/<conversation_id>/messages/<message_id>')
def get_message(conversation_id: str, message_id: str):
    result = get_message_service(conversation_id, message_id)
    return jsonify({"message": result.model_dump(by_alias=True, mode='json')})


@bp.delete('/conversations/<conversation_id>/messages/<message_id>')
def delete_message(conversation_id: str, message_id: str):
    delete_message_service(conversation_id, message_id)
    return '', 204
