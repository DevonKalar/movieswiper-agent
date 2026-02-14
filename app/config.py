import os

class BaseConfig:
  MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ms-agent')
  APP_ENV = os.getenv('APP_ENV', 'development')

class DevConfig(BaseConfig):
  DEBUG = True

class ProdConfig(BaseConfig):
  DEBUG = False

def get_config():
  return ProdConfig() if os.getenv('APP_ENV') == 'production' else DevConfig()