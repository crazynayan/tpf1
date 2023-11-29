import os
from base64 import b64encode
from typing import Optional, Dict

from firestore_ci import FirestoreDocument
from flask import g, Response, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash

from d21_backend.config import config
from d21_backend.p1_utils.domain import is_domain_valid
from d21_backend.p2_assembly.mac2_data_macro import init_macros
from d21_backend.p2_assembly.seg9_collection import init_seg_collection
from d21_backend.p3_db.pnr import Pnr
from d21_backend.p7_flask_app import tpf1_app
from d21_backend.p7_flask_app.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(email: str, password: str) -> bool:
    g.current_user = User.get_by_email(email)
    return g.current_user is not None and g.current_user.check_password(password)


@basic_auth.error_handler
def basic_auth_error() -> Response:
    return error_response(401)


@tpf1_app.route("/tokens", methods=["POST"])
@basic_auth.login_required
def generate_token() -> Response:
    g.current_user.generate_token()
    init_seg_collection()
    init_macros()
    Pnr.init_pdequ()
    user_response: dict = {
        "email": g.current_user.email,
        "id": g.current_user.id,
        "initial": g.current_user.initial,
        "role": g.current_user.role,
        "token": g.current_user.token,
        "domain": g.current_user.domain,
    }
    return jsonify(user_response)


@token_auth.verify_token
def verify_token(token: str) -> bool:
    g.current_user = User.get_by_token(token) if token else None
    if g.current_user is not None:
        init_seg_collection()
        init_macros()
        Pnr.init_pdequ()
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error() -> Response:
    return error_response(401)


class User(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.email: str = str()  # email address is the username
        self.initial: str = str()  # 2 character initial in uppercase
        self.role: str = config.MEMBER  # Role of the user. Refer config.ROLES
        self.domain: str = config.DOMAIN  # Domain of the user. Refer config.DOMAINS
        self.password_hash: str = config.DEFAULT_PASSWORD
        self.token: str = config.DEFAULT_TOKEN

    def __repr__(self):
        return f"{self.email}|{self.initial}|{self.role}"

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
        user_dict["email"] = user.email
        return user_dict

    @classmethod
    def get_by_token(cls, token: str) -> Optional["User"]:
        return cls.objects.filter_by(token=token).first()

    @classmethod
    def get_by_email(cls, email: str) -> Optional["User"]:
        return cls.objects.filter_by(email=email).first()


User.init()


def create_user(email: str, initial: str, domain: str):
    if not isinstance(email, str) or sum(1 for char in email if char == "@") != 1 or "|" in email:
        print(f"Invalid email - {email}")
        return
    if not is_domain_valid(domain):
        print(f"Invalid domain - {domain}")
        return
    if User.objects.filter_by(email=email).first():
        print(f"Email already exists")
        return
    if not isinstance(initial, str) or len(initial) != 2 or not initial.isalpha():
        print(f"Initial should be 2 character alphabet string")
        return
    if User.objects.filter_by(initial=initial).first():
        print(f"Initial already exits")
        return
    user = User()
    user.email = email
    user.initial = initial.upper()
    user.domain = domain
    password = b64encode(os.urandom(24)).decode()
    user.set_password(password)
    user.set_id(email.replace("@", "_").replace(".", "-"))
    user.save()
    print(f"User {user.email} created with initial {user.initial}. Your password is {password}")
    return
