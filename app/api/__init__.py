from .health import bp as health_bp
from .chat.routes import bp as chat_bp

def register_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(chat_bp, url_prefix="/chat")
