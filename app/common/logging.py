import sentry_sdk
import os
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask

sentry_sdk.init(
  dsn=os.getenv('SENTRY_DSN'),
  integrations=[FlaskIntegration()],
  traces_sample_rate=1.0,
)

def register_logging(app: Flask):
  app.logger.info('Logging initialized')