from flask import Flask, url_for
from flask_caching import Cache
from flask_restx import Api, Namespace
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import migrate
from flask_cors import CORS
from config import getConfig
from importlib import import_module

from app.src.db.driver import init_db

config = getConfig()

app = Flask(__name__)
CORS(app)
limiter = Limiter(app, key_func=get_remote_address, default_limits=[])
app.config.from_object(config)

db = SQLAlchemy(app)
init_db(db)
# migrate = Migrate(app, db)

cache = Cache(app)

class Custom_API(Api):
    # override specs url to be relative not absolute
    @property
    def specs_url(self):
        return url_for(self.endpoint('specs'), _external=False)

api = Custom_API(
    app,
    version=app.config['VERSION'],
    title='FortBookie API',
    description='FortBookie SwaggerUI',
    doc='/api/',
    validate=True
)

order = ['users', 'admin']
for name in order:
    endpoint = import_module(f'app.src.endpoints.{name}')

    for name in dir(endpoint):
        if name.endswith('_api'):
            attribute = getattr(endpoint, name)
            if isinstance(attribute, Namespace):
                api.add_namespace(attribute)
