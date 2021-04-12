import os
import tempfile
import git

class BaseConfig(object):
    VERSION = f'1.0.{git.Repo().head.object.hexsha[:6]}'
    HOST = '0.0.0.0'
    PORT = 5000
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTX_MASK_SWAGGER = False
    ERROR_404_HELP = False
    TESTING = False
    SWAGGER_UI_DOC_EXPANSION = 'list'
    JWT_SECRET = 'BC37C869237A283F33E7437F90136937B4D0A16FA50EBB329B5E2A93D4D5DF9E'


    CACHE_TYPE = 'redis'
    # CACHE_REDIS_PASSWORD = ''
    CACHE_REDIS_HOST = 'redis'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0


class prodConfig(BaseConfig):
    CONFIG = 'prod'
    DOMAIN = 'https://app.fortbookie.com'

    ENV = 'production'


class stagingConfig(BaseConfig):
    CONFIG = 'staging'
    DOMAIN = 'beta.fortbookie.com'

    ENV = 'production'


class devConfig(BaseConfig):
    CONFIG = 'dev'
    DOMAIN = 'http://localhost'

    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:noder@localhost/fortBookie'


class testConfig(BaseConfig):
    CONFIG = 'test'
    DOMAIN = 'http://localhost'

    ENV = 'production'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{tempfile.mkstemp()[1]}'


configList = {
    'prod': prodConfig(),
    'staging': stagingConfig(),
    'dev': devConfig(),
    'test': testConfig()
}


def getConfig():
    # get environment dynamically later
    return configList['dev']

