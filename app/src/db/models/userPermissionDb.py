from app import db
from app.src.db.models.permissionDb import getPermissionById


class UserPermission(db.Model):
    __tablename__ = 'user_permission'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    permission_id = db.Column(db.Integer(), db.ForeignKey('permission.id'), nullable=False)
    

    def __init__(self, user_id, permission_id=2):
        self.user_id = user_id
        self.permission_id = permission_id

    def save(self):
        db.session.add(self)
        db.session.commit()


def updateUserPermission(user_id, permission_id):
    user_permission = UserPermission.query.filter_by(user_id=user_id).first()
    user_permission.permission_id = permission_id
    db.session.commit()


def getPermissionByUserId(user_id):
    user_permission = UserPermission.query.filter_by(user_id=user_id).first()
    permission = getPermissionById(user_permission.permission_id)
    return permission


def deleteUserPermission(user_id):
    user_permission = UserPermission.query.filter_by(user_id=user_id).first()
    db.session.delete(user_permission)
    db.session.commit()