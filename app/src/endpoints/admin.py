from flask import request
from flask_restx import Namespace, Resource, fields, Model
from bcrypt import checkpw
from password_strength import PasswordPolicy
import datetime
import json
import pyotp
import base64

from app import app
# from app import app, cache, limiter
from app.src.utils import errorResponse, successResponse
from app.src.jwtHandler import authRequestParser, auth
from app.src.db.models.usersDb import findUserById, findUserByEmail, deleteUser, getUserRole, findAllUsers
from app.src.db.models.userPermissionDb import deleteUserPermission, getPermissionByUserId, updateUserPermission


admin_api = Namespace('admin')

default_user = {
    'email': 'testadmin@redon.com',
    'userName': 'testAdminName1',
    'password': 'testpassword!1',
}

adminInfoUserModel = admin_api.model('UserInfo', {
    'id': fields.Integer(),
    'email': fields.String(),
    'role': fields.String()
})

adminInfoAllUserModel = admin_api.model('UserInfo', {
    'id': fields.Integer(),
    'email': fields.String()
    # 'role': fields.String()
})

adminUpdateUserModel = admin_api.model('UserUpdate', {
    #'email': fields.String(example=default_user['email'], pattern=email_regex),
    'role': fields.Integer()
})


def block_if_not_admin(user):
    if getUserRole(user) != 'admin':
        errorResponse(admin_api, "Unauthorized", 403)
        # errorResponse(admin_api, "You are not authorized to perform this action", 403)


@admin_api.route('/users/<user_id>')
class Info(Resource):

    @admin_api.doc(responses={
        200: 'User is returned',
        400: 'Bad request',
        403: 'Unauthorized',
        404: 'Not found'
    })
    @admin_api.expect(authRequestParser)
    @admin_api.marshal_with(adminInfoUserModel)
    def get(self, user_id):
        '''Get user info by id'''

        admin = auth(request, admin_api)
        block_if_not_admin(admin)

        user = findUserById(user_id)

        if not user:
            errorResponse(admin_api, "User with such id does not exist", 404)

        user_json = findUserById(user_id).__dict__
        user_json['role'] = getUserRole(user)

        return user_json


@admin_api.route('/users')
class Info(Resource):

    @admin_api.doc(responses={
        200: 'Users are returned',
        400: 'Bad request',
        403: 'Unauthorized',
        404: 'Not found'
    })
    @admin_api.expect(authRequestParser)
    @admin_api.marshal_with(adminInfoAllUserModel)
    def get(self):
        '''Get list of all users'''

        admin = auth(request, admin_api)
        block_if_not_admin(admin)

        return findAllUsers()


@admin_api.route('/users/delete/<user_id>')
class Delete(Resource):

    @admin_api.doc(responses={
        204: 'User is deleted',
        403: 'Unauthorized',
        404: 'Not found'
    })
    @admin_api.expect(authRequestParser)
    def delete(self, user_id):
        '''Delete user by id'''

        admin = auth(request, admin_api)
        block_if_not_admin(admin)

        user = findUserById(user_id)

        if not user:
            errorResponse(admin_api, "User with such id does not exist", 404)

        if getUserRole(user) == 'admin':
            errorResponse(admin_api, "You cannot delete other admins", 403)

        deleteUserPermission(user_id)
        deleteUser(user)

        return None, 204


@admin_api.route('/update/users/<user_id>')
class UpdateUser(Resource):

    @admin_api.doc(responses={
        200: 'User is successfully updated',
        400: 'Bad request',
        403: 'Forbidden',
        422: 'Validation error'
    })
    @admin_api.expect(authRequestParser, adminUpdateUserModel)
    @admin_api.marshal_with(adminUpdateUserModel, skip_none=True)
    def put(self, user_id):
        '''Update user profile'''

        admin = auth(request, admin_api)
        block_if_not_admin(admin)

        user = findUserById(user_id)

        if not user:
            errorResponse(admin_api, "User with such id does not exist", 404)

        if getUserRole(user) == 'admin':
            errorResponse(admin_api, "You cannot update other admins", 403)

        response = request.json

        try:
            user.update(response)
            updateUserPermission(user.id, response['role'])
        except Exception as e:
            return errorResponse(admin_api, str(e))

        return user
        #return successResponse('User updated successfully', 201)
