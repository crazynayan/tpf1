from flask import Flask
from flask_cors import CORS

from config import Config

tpf1_app = Flask(__name__)
tpf1_app.config.from_object(Config)
cors = CORS(tpf1_app)

# noinspection PyPep8
from flask_app import routes, auth
