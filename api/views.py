from bson import ObjectId
import jwt
from functools import wraps
from jwt import DecodeError, ExpiredSignature
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from flask.ext import restful
from flask.ext.restful import reqparse
from mongoengine import ValidationError, NotUniqueError
from api import status
from api.models import User
from app import SECRET_KEY


api_v1_bp = Blueprint('api', __name__)

api_v1 = restful.Api(api_v1_bp, prefix="/api/v1")


def create_token(user):
    payload = {
        'sub': str(user.id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=1),
    }
    token = jwt.encode(payload, SECRET_KEY)
    return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, SECRET_KEY, algorithms='HS256')


def jwt_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return response
        request.user = User.objects.get(id=ObjectId(payload['sub']))
        return f(*args, **kwargs)

    return decorated_function


class SignUpAPI(restful.Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')
        super(SignUpAPI, self).__init__()

    def post(self):
        req_kwargs = self.reqparse.parse_args()
        user = User(email=req_kwargs['email'])
        user.hash_password(req_kwargs['password'])
        try:
            user.save()
        except ValidationError as e:
            return {'message': e.message}, status.HTTP_400_BAD_REQUEST
        except NotUniqueError:
            return {'message': 'This email already registered'}, status.HTTP_409_CONFLICT
        return {'message': 'Success'}, status.HTTP_200_OK


class SignInAPI(SignUpAPI):
    def post(self):
        req_kwargs = self.reqparse.parse_args()
        email = req_kwargs['email']
        password = req_kwargs['password']
        user = User.objects.filter(email=email).first()
        if not user:
            return {"message": "Invalid username/password"}, status.HTTP_401_UNAUTHORIZED
        if user.verify_password(password):
            token = create_token(user)
            return {'token': token}, status.HTTP_200_OK
        return {"message": "Invalid username/password"}, status.HTTP_401_UNAUTHORIZED


class ChangePasswordAPI(restful.Resource):
    method_decorators = [jwt_token_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('old_password', type=str, location='json')
        self.reqparse.add_argument('new_password', type=str, location='json')
        self.reqparse.add_argument('new_password_confirm', type=str, location='json')
        super(ChangePasswordAPI, self).__init__()

    def patch(self):
        req_kwargs = self.reqparse.parse_args()
        user = request.user
        old_password = req_kwargs['old_password']
        new_password = req_kwargs['new_password']
        new_password_confirm = req_kwargs['new_password_confirm']
        if not user.verify_password(old_password):
            return {'message': 'Incorrect current password'}, status.HTTP_400_BAD_REQUEST
        if not new_password == new_password_confirm:
            return {'message': 'Passwords do not match'}, status.HTTP_400_BAD_REQUEST
        user.hash_password(new_password)
        user.save()
        return {'message': 'Success'}, status.HTTP_200_OK


class ProtectedUrlAPI(restful.Resource):
    method_decorators = [jwt_token_required]

    def get(self):
        user = request.user
        return {'message': 'Hi {}, you got protected data'.format(user.email)}, status.HTTP_200_OK


api_v1.add_resource(SignUpAPI, '/auth/signup', endpoint='user.signup')
api_v1.add_resource(SignInAPI, '/auth/signin', endpoint='user.signin')
api_v1.add_resource(ChangePasswordAPI, '/user/change_password', endpoint='user.change.password')
api_v1.add_resource(ProtectedUrlAPI, '/protected_data', endpoint='protected')

