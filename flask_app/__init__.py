from flask import Flask

from config import Config

tpf1_app = Flask(__name__)
tpf1_app.config.from_object(Config)

# noinspection PyPep8
from flask_app import routes, auth
