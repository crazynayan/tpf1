from flask import Flask
from flask_cors import CORS

from config import Config
from p2_assembly.seg8_listing import create_lxp

tpf1_app = Flask(__name__)
tpf1_app.config.from_object(Config)
cors = CORS(tpf1_app)

# noinspection PyPep8
from p7_flask_app import routes, auth, template_routes

from p7_flask_app.api import bp as api_bp

tpf1_app.register_blueprint(api_bp, url_prefix="/api")


@tpf1_app.shell_context_processor
def make_shell_context():
    from config import config
    import tpf
    from p1_utils.file_line import File
    from p2_assembly.seg8_listing import create_listing_commands, write_tmp_output, LstCmd
    from p2_assembly.seg9_collection import SegLst, seg_collection
    from p3_db.test_data import TestData
    from p3_db import template_crud, template_merge, test_data_get, template_models, test_data_variations
    from p4_execution.ex5_execute import TpfServer
    from p7_flask_app.auth import User
    from p7_flask_app import routes
    return {
        "TestData": TestData,
        "TpfServer": TpfServer,
        "User": User,
        "client": tpf1_app.test_client(),
        "config": config,
        "create_listing_commands": create_listing_commands,
        "File": File,
        "SegLst": SegLst,
        "LstCmd": LstCmd,
        "write_tmp_output": write_tmp_output,
        "create_lxp": create_lxp,
        "seg_collection": seg_collection,
        "routes": routes,
        "tpf": tpf,
        "template": template_crud,
        "merge": template_merge,
        "test_data_get": test_data_get,
        "templates": template_models,
        "td_variations": test_data_variations,
    }
