import os

class BaseConfig:
  MONGO_URI = os.getenv('MONGO_URL', 'mongodb://localhost:27017/ms-agent')
  APP_ENV = os.getenv('APP_ENV', 'development')
  JWT_SECRET = os.getenv('JWT_SECRET', '')

class DevConfig(BaseConfig):
  DEBUG = True

class ProdConfig(BaseConfig):
  DEBUG = False

def get_config():
  return ProdConfig() if os.getenv('APP_ENV') == 'production' else DevConfig()