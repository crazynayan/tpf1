import os
from base64 import b64encode
from typing import Optional, Dict

from werkzeug.security import generate_password_hash, check_password_hash

from config import config
from firestore.firestore_ci import FirestoreDocument


class User(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.email: str = ''
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


User.init()


def get_user_by_token(token: str) -> Optional[User]:
    user: Optional[User] = User.objects.filter_by(token=token).first()
    return user


def get_user_by_email(email: str) -> Optional[User]:
    user: Optional[User] = User.objects.filter_by(email=email).first()
    return user


def get_user_dict_by_id(doc_id: str) -> Optional[Dict[str, str]]:
    user_dict: Dict[str, str] = dict()
    user: Optional[User] = User.get_by_id(doc_id)
    if not user:
        return None
    user_dict['email'] = user.email
    return user_dict
