import sentry_sdk
import os
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask

def register_logging(app: Flask):
  if (dsn := os.getenv('SENTRY_DSN', '')).startswith('https://'):
    sentry_sdk.init(
      dsn=dsn,
      integrations=[FlaskIntegration()],
      traces_sample_rate=1.0,
    )
  app.logger.info('Logging initialized')