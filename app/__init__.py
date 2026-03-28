from flask import Flask
from .config import get_config
from .extensions import init_mongo
from .api import register_blueprints
from .common.error_handler import register_error_handlers
from .common.request_context import register_request_context
from .common.logging import register_logging

def create_app():
  app = Flask(__name__)
  app.config.from_object(get_config())

  register_request_context(app)
  register_error_handlers(app)
  register_logging(app)

  init_mongo(app)

  register_blueprints(app)

  return app