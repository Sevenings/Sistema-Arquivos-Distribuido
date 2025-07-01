import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DATABASE_PATH = f'sqlite:///{basedir}/data/data.db'
    TEMPO_HEARTBEAT = 60 # segundos

class DevelopmentConfig(Config):
    DATABASE_PATH = f'sqlite:///{basedir}/data/dev_data.db'
    TEMPO_HEARTBEAT = 10 # segundos

class TestConfig(Config):
    DATABASE_PATH = f'sqlite:///{basedir}/data/test_data.db'
    TEMPO_HEARTBEAT = 10 # segundos

class ProductionConfig(Config):
    DATABASE_PATH = f'sqlite:///{basedir}/data/data.db'
    TEMPO_HEARTBEAT = 60 # segundos


configs = {
        "default": DevelopmentConfig,
        "test": TestConfig,
        "development": DevelopmentConfig,
        "production": ProductionConfig
        }

config = configs["default"]