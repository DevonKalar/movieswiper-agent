from flask import Flask
from .config import get_config
from .extensions import init_mongo
from .api import register_blueprints
from .common.errors import register_error_handlers
from .common.request_context import register_request_context

def create_app():
  app = Flask(__name__)
  app.config.from_object(get_config())

  register_request_context(app)

  init_mongo(app)

  register_blueprints(app)
  register_error_handlers(app)

  return app