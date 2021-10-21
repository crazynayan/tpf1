from flask import Flask
from flask_cors import CORS

from config import Config

tpf1_app = Flask(__name__)
tpf1_app.config.from_object(Config)
cors = CORS(tpf1_app)

# noinspection PyPep8
from p7_flask_app import routes, auth

from p7_flask_app.api import bp as api_bp

tpf1_app.register_blueprint(api_bp, url_prefix="/api")


@tpf1_app.shell_context_processor
def make_shell_context():
    from p3_db.test_data import TestData
    from p4_execution.ex5_execute import TpfServer
    from p7_flask_app.auth import User
    from config import config
    from tpf import create_user
    from p2_assembly.seg7_listing import create_listing_lines
    return {
        "TestData": TestData,
        "TpfServer": TpfServer,
        "User": User,
        "create_user": create_user,
        "client": tpf1_app.test_client(),
        "config": config,
        "create_listing_lines": create_listing_lines,
    }
