from flask import Flask
from flask_login import LoginManager

from d29_frontend.config import Config

tpf2_app: Flask = Flask(__name__)
tpf2_app.config.from_object(Config)
login = LoginManager(tpf2_app)
login.login_view = 'login'

# noinspection PyPep8
from d29_frontend.flask_app import routes
from d29_frontend.flask_app.user import login, logout
from d29_frontend.flask_app import test_data_routes, template_routes, profiler_routes
