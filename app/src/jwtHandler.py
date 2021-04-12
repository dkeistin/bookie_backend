from flask_restx import reqparse
import datetime
import jwt
from flask import g

from app.src.db.models.usersDb import findUserById
from app import app
from app.src.utils import errorResponse


authRequestParser = reqparse.RequestParser().add_argument(
    'Authorization', required=True, location='headers'
)
authOptionalRequestParser = reqparse.RequestParser().add_argument(
    'Authorization', location='headers'
)


def jwtError(namespace, message):
    # app.logger.error(f'JWT Error: {message}')
    errorResponse(namespace, f'JWT Error: {message}', 403)


def decode(token):
    return jwt.decode(
        token,
        app.config['JWT_SECRET'],
        algorithms=['HS256']
    )


def generateJWT(user):
    now = datetime.datetime.utcnow()
    jwt_token = jwt.encode(
        {
            'iat': now,
            'exp': now + datetime.timedelta(hours=1),
            'user_id': user.id
        },
        app.config['JWT_SECRET'],
        algorithm='HS256'
    )

    return jwt_token


def auth(request, namespace, requiredAuth=True):
    '''
        Provides a wrapper to auth users with JWT
        Gets user id from decoded token and pulls user object from db to return it.
        throws exception if requiredAuth
    '''

    try:

        token = request.headers.get('Authorization')
        if token:
            user_id = decode(token)['user_id']
            user = findUserById(user_id)

            if not user:
                raise Exception(f'User with id {user_id} is not found')

            # app.logger.info(
            #     f'{request.method} {request.full_path} {user}',
            #     extra={
            #         'tags': {
            #             'service': 'jwt'
            #         }
            #     }
            # )
            g.user = user

            return user
        else:
            if requiredAuth:
                raise Exception('JWT not found in Authorization header')

    except Exception as e:
        jwtError(namespace, e)