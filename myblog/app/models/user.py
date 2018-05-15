"""
myblog是单人博客，user即admin
"""


from . import db, Mixin

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class UserModel(db.Model, Mixin, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(16), nullable=False)
    password_hash = db.Column(db.Unicode(128), nullable=False)

    @property
    def password(self):
        raise AttributeError('不要尝试获取密码')

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_user(cls, name):
        return cls.query.filter_by(name=name).first()


def create_user(username, password):
    user = UserModel(username=username, password=password)
    user.save()


def get_user(user_id: int):
    user = UserModel.query.filter_by(int(user_id))
    return user