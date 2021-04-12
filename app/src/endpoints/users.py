from flask import request
from flask_restx import Namespace, Resource, fields, Model
from bcrypt import checkpw
from password_strength import PasswordPolicy
import secrets
import datetime
import json
import pyotp
import base64

from app import app, cache, limiter
from app.src.utils import errorResponse, successResponse
from app.src.jwtHandler import generateJWT, authRequestParser, auth
from app.src.db.models.usersDb import findUserByEmail, findUserByUserName, createUser, deleteUser, getUserRole
from app.src.db.models.userPermissionDb import UserPermission, deleteUserPermission, getPermissionByUserId  # check if userPermission can be removed from here


import re


class StrictModel(Model):
    '''
        As flask_restx doesnt have option to set strict models, we override _schema prop
        to have additionalProperties = False
    '''

    @property
    def _schema(self):
        old = super()._schema
        old['additionalProperties'] = False
        return old


users_api = Namespace('user')
password_policy = PasswordPolicy.from_names(length=8, numbers=1, special=1)

email_regex = '[^@]+@[^@]+\\.[^@]+'
phone_regex = '^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\\s\\./0-9]*$'


default_user = {
    'email': 'testuser@redon.com',
    'userName': 'testUserName1',
    'password': 'testpassword!1',
}


userLoginModel = users_api.model('LoginUser', {
    'userName': fields.String(example=default_user['userName'], required=True),
    'password': fields.String(example=default_user['password'], required=True)
})

userCreateModel = users_api.model('CreateUser', {
    'email': fields.String(example=default_user['email'], pattern=email_regex, required=True),
    'userName': fields.String(example=default_user['userName'], required=True),
    'password': fields.String(example=default_user['password'], required=True)
})

userInfoModel = users_api.model('UserInfo', {
    'id': fields.Integer(),
    'email': fields.String(),
    'userName': fields.String()
})

userUpdateModel = users_api.model('UserUpdate', {
    #'email': fields.String(example=default_user['email'], pattern=email_regex),
    'userName': fields.String(example=default_user['userName'])
    # 'lastName': fields.String(example=default_user['lastName'])
})

changePasswordModel = users_api.model('ChangePassword', {
    'old_password': fields.String(example=default_user['password'], required=True),
    'new_password': fields.String(example=default_user['password'], required=True)
})


@users_api.route('/login')
class Login(Resource):

    # decorators = [limiter.limit('5/15minute')]

    @users_api.doc(responses={
        200: 'User is successfully logged in',
        400: 'Bad request',
        404: 'User with such email and password was not found'
    })
    @users_api.expect(userLoginModel)
    def post(self):
        '''Login with specified credentials'''

        userName = request.json.get('userName')
        password = request.json.get('password')

        user = findUserByUserName(userName)

        if user is None or not checkpw(password.encode('utf8'), user.password.encode('utf8')):
            errorResponse(users_api, 'User with such username or password was not found', 404)

        return {'Authorization': generateJWT(user)}


@users_api.route('/register')
class Register(Resource):

    @users_api.doc(responses={
        200: 'User registered successfully',
        400: 'Bad request',
        422: 'User with such email already exists'
    })
    @users_api.expect(userCreateModel)
    def post(self):
        '''Register a new user'''

        email = request.json.get('email')
        userName = request.json.get('userName')
        password = request.json.get('password')

        if len(password_policy.test(password)) != 0:
            errorResponse(
                users_api, 'Password should be at least 8 characters long, contain 1 digit and 1 special char'
            )

        user = None if not findUserByEmail(email) else findUserByUserName(userName)
        if user:
            errorResponse(users_api, f'User with email {email} or {userName} already exists')

        try:
            user = createUser({
                'email': email,
                'userName': userName,
                'password': password
            })

            UserPermission(user.id).save()

        except Exception as e:
            errorResponse(users_api, str(e))

        return successResponse('User registered successfully')


@users_api.route('/update')
class UpdateUser(Resource):

    @users_api.doc(responses={
        200: 'User is successfully updated',
        400: 'Bad request',
        403: 'Forbidden',
        422: 'Validation error'
    })
    @users_api.expect(authRequestParser, userUpdateModel)
    @users_api.marshal_with(userUpdateModel, skip_none=True)
    def put(self):
        '''Update user profile'''

        user = auth(request, users_api)

        try:
            user.update(request.json)
        except Exception as e:
            return errorResponse(users_api, str(e))

        return user
        #return successResponse('User updated successfully', 201)


@users_api.route('/delete')
class Delete(Resource):

    @users_api.doc(responses={
        204: 'User is deleted',
        403: 'Unauthorized'
    })
    @users_api.expect(authRequestParser)
    def delete(self):
        '''Delete current user'''

        user = auth(request, users_api)
        deleteUserPermission(user.id)
        deleteUser(user)

        return None, 204


@users_api.route('/info')
class Info(Resource):

    @users_api.doc(responses={
        200: 'User is returned',
        400: 'Bad request',
        403: 'Forbidden'
    })
    @users_api.expect(authRequestParser)
    @users_api.marshal_with(userInfoModel)
    def get(self):
        '''Get current user info'''

        user = auth(request, users_api)

        return user


@users_api.route('/changePassword')
class ChangePassword(Resource):

    @users_api.doc(responses={
        201: 'Updated user password',
        400: 'Bad request',
        403: 'Unauthorized'
    })
    @users_api.expect(authRequestParser, changePasswordModel)
    def post(self):
        '''Change user password'''

        user = auth(request, users_api)

        old_password = request.json['old_password']
        new_password = request.json['new_password']

        if not checkpw(old_password.encode('utf8'), user.password.encode('utf8')):
            errorResponse(users_api, 'Wrong old password', 403)

        if len(password_policy.test(new_password)) != 0:
            errorResponse(
                users_api, 'Password should be at least 8 characters long, contain 1 digit and 1 special char'
            )

        user.updatePassword(new_password)
        return successResponse('User password has beend updated', 201)