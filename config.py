import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DATABASE_PATH = f'sqlite:///{basedir}/data/data.db'

class DevelopmentConfig(Config):
    DATABASE_PATH = f'sqlite:///{basedir}/data/dev_data.db'

class TestConfig(Config):
    DATABASE_PATH = f'sqlite:///{basedir}/data/test_data.db'

class ProductionConfig(Config):
    DATABASE_PATH = f'sqlite:///{basedir}/data/data.db'


configs = {
        "default": DevelopmentConfig,
        "test": TestConfig,
        "development": DevelopmentConfig,
        "production": ProductionConfig
        }
