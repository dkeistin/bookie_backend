import os
from app import app

config = os.getenv('ENV')

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'], port=app.config['PORT']
    )