from flask import g, Response, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from firestore.auth import User, get_user_by_email, get_user_by_token
from flask_app import tpf1_app
from flask_app.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(email: str, password: str) -> bool:
    user: User = get_user_by_email(email)
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)


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
    g.current_user = get_user_by_token(token) if token else None
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error() -> Response:
    return error_response(401)
