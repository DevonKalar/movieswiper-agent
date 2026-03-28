import uuid
from flask import Flask, g, request


def attach_context():
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    g.user_id = request.headers.get('X-User-ID')
    g.body = request.get_json(silent=True) or {}


def register_request_context(app: Flask):
    app.before_request(attach_context)
