import os
from base64 import b64encode
from typing import Optional, Dict

from firestore_ci import FirestoreDocument
from flask import g, Response, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash

from config import config
from p7_flask_app import tpf1_app
from p7_flask_app.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(email: str, password: str) -> bool:
    g.current_user = User.get_by_email(email)
    return g.current_user is not None and g.current_user.check_password(password)


@basic_auth.error_handler
def basic_auth_error() -> Response:
    return error_response(401)


@tpf1_app.route('/tokens', methods=['POST'])
@basic_auth.login_required
def generate_token() -> Response:
    token = g.current_user.generate_token()
    return jsonify({'token': token})


@token_auth.verify_token
def verify_token(token: str) -> bool:
    g.current_user = User.get_by_token(token) if token else None
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error() -> Response:
    return error_response(401)


class User(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.email: str = str()
        self.password_hash: str = config.DEFAULT_PASSWORD
        self.token: str = config.DEFAULT_TOKEN

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_token(self) -> str:
        self.token = b64encode(os.urandom(24)).decode()
        self.save()
        return self.token

    def revoke_token(self) -> None:
        self.token = b64encode(os.urandom(24)).decode()

    @classmethod
    def get_user(cls, doc_id: str) -> Optional[Dict[str, str]]:
        user: Optional[cls] = cls.get_by_id(doc_id)
        if not user:
            return None
        user_dict: Dict[str, str] = dict()
        user_dict['email'] = user.email
        return user_dict

    @classmethod
    def get_by_token(cls, token: str) -> Optional['User']:
        return cls.objects.filter_by(token=token).first()

    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        return cls.objects.filter_by(email=email).first()


User.init()
