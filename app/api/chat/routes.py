from flask import Blueprint
from .controllers import get_messages, create_message

bp = Blueprint('chat', __name__)

@bp.get('/messages')
def get_messages():
  return get_messages()

@bp.post('/messages')
def create_message():
  return create_message()