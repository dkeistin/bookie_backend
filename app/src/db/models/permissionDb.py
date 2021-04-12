from sqlalchemy.event import listen
from sqlalchemy import event

from app import db


class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())
    

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def save(self):
        db.session.add(self)
        db.session.commit()


@event.listens_for(Permission.__table__, 'after_create')
def insert_default_roles(*args, **kwargs):

    db.session.add(Permission('admin', 'Admin Privileges'))
    db.session.add(Permission('user', 'User Privileges'))
    db.session.commit()


def getPermissionById(id):
    return Permission.query.filter_by(id=id).first()