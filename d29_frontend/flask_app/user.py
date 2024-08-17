from functools import wraps
from typing import Optional

from flask import flash, redirect, url_for, render_template, request, Response, make_response, current_app
from flask_login import UserMixin, current_user, login_user, logout_user
from flask_wtf import FlaskForm
from munch import Munch
from urllib.parse import urlparse as url_parse
from wtforms import PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired

from d29_frontend.config import Config
from d29_frontend.flask_app import tpf2_app, login
from d29_frontend.flask_app.server import Server


def cookie_login_required(route_function):
    @wraps(route_function)
    def decorated_route(*args, **kwargs):
        user_data = request.cookies.get("user_data")
        if not user_data:
            return current_app.login_manager.unauthorized()
        if current_user.is_authenticated:
            return route_function(*args, **kwargs)
        user = load_user(user_data)
        login_user(user=user)
        return route_function(*args, **kwargs)

    return decorated_route


def error_check(route_function):
    @wraps(route_function)
    def decorated_route(*args, **kwargs):
        try:
            return route_function(*args, **kwargs)
        except Server.Timeout:
            flash("Session timeout. Please login again.")
            logout_user()
            return redirect(url_for("login"))
        except Server.SystemError:
            flash("System Error. Unable to proceed.")
            return redirect(url_for("home"))

    return decorated_route


class User(UserMixin):
    SEPARATOR: str = "|"

    def __init__(self, email: str = None, api_key: str = None, initial: str = None, role: str = None,
                 domain: str = None):
        super().__init__()
        self.email: str = email.replace(self.SEPARATOR, "") if email else str()
        self.api_key: str = api_key if api_key else str()
        self.initial: str = initial if initial else str()
        self.role: str = role if role else str()
        self.domain: str = domain if domain else str()

    def __repr__(self):
        return f"{self.email}{self.SEPARATOR}{self.api_key}{self.SEPARATOR}{self.initial}{self.SEPARATOR}{self.role}" \
               f"{self.SEPARATOR}{self.domain}"

    def check_password(self, password: str) -> bool:
        user_response: dict = Server().authenticate(self.email, password)
        if not user_response:
            return False
        try:
            self.email = user_response["email"].replace(self.SEPARATOR, "")
            self.initial = user_response["initial"].replace(self.SEPARATOR, "")
            self.role = user_response["role"].replace(self.SEPARATOR, "")
            self.domain = user_response["domain"].replace(self.SEPARATOR, "")
            self.api_key = user_response["token"].replace(self.SEPARATOR, "")
        except KeyError:
            return False
        return True

    def get_id(self) -> str:
        return str(self)


@login.user_loader
def load_user(user_data: str) -> Optional[User]:
    if User.SEPARATOR not in user_data:
        return None
    email, token, initial, role, domain = user_data.split(User.SEPARATOR)
    return User(email, token, initial, role, domain)


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


@tpf2_app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("login.html", title="TPF Analyzer", form=form)
    user = User(form.email.data.lower())
    if not user.check_password(form.password.data):
        flash(f"Invalid email or password.")
        return redirect(url_for("login"))
    login_user(user=user)
    next_page = request.args.get("next")
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for("get_my_test_data")
    response: Response = make_response(redirect(next_page))
    response.set_cookie("user_data", str(user), max_age=Config.TOKEN_EXPIRY, secure=Config.CI_SECURITY, httponly=True,
                        samesite="Strict")
    return response


@tpf2_app.route("/logout")
def logout() -> Response:
    if current_user.is_authenticated:
        logout_user()
    response: Response = make_response(redirect(url_for("home")))
    response.set_cookie("user_data", str(), max_age=0, secure=Config.CI_SECURITY, httponly=True, samesite="Strict")
    return response


def flash_message(response: Munch) -> None:
    if response.message:
        flash(response.message)
        return
    if not response.get("error", True):
        return
    for _, error_msg in response.error_fields.items():
        if error_msg:
            flash(error_msg)
            return
    flash("System Error. No changes made.")
    return
