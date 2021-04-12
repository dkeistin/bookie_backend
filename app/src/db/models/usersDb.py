from sqlalchemy.exc import IntegrityError
from bcrypt import gensalt, hashpw

from app import db, app
from app.src.db.models.userPermissionDb import getPermissionByUserId


class User(db.Model):
    __tablename__ = 'users'


    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(), unique=True)
    userName = db.Column(db.String(), unique=True)
    password = db.Column(db.String(), nullable=False)


    def __init__(self, data):
        self.email = data.get('email')
        self.userName = data.get('userName')
        self.password = hashpw(
            data.get('password').encode('utf8'), gensalt()
        ).decode('utf8')

    
    def __repr__(self):
        return f'User {self.id}> [{self.email}]'


    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()

            if 'users_email_key' in e.args[0]:
                raise Exception(
                    f'User with email {data.get("email")} already exists'
                )


    def updatePassword(self, password):
        self.password = hashpw(
            password.encode('utf8'), gensalt()
        ).decode('utf8')
        db.session.commit()


def createUser(data):
    try:
        user = User(data)
        db.session.add(user)
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()

        if 'users_email_key' in e.args[0]:
            raise Exception(
                f'User with email {data.get("email")} already exists'
            )

    except Exception as e:
        raise e

    return user


def findUserById(id):
    return User.query.filter_by(id=id).first()


def findUserByEmail(email):
    return User.query.filter_by(email=email).first()


def findUserByUserName(userName):
    return User.query.filter_by(userName=userName).first()


def deleteUser(user):
    db.session.delete(user)
    db.session.commit()


def getUserRole(user):
    role = getPermissionByUserId(user.id)
    return role.name


def findAllUsers():
    return User.query.all()



