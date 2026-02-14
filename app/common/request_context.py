import uuid
from flask import g, request
from app import app

def attach_context():
  g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
  g.user_id = request.headers.get('X-User-ID')

def register_request_context():
  app.before_request(attach_context)
