from mongoengine import Document
from mongoengine import fields
from app import flask_bcrypt


class User(Document):
    email = fields.EmailField(required=True, unique=True)
    password = fields.StringField(required=True)

    def hash_password(self, password):
        self.password = flask_bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return flask_bcrypt.check_password_hash(self.password, password)
