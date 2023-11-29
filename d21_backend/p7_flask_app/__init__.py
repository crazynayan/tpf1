from flask import Flask
from flask_cors import CORS

from d21_backend.config import Config

tpf1_app = Flask(__name__)
tpf1_app.config.from_object(Config)
cors = CORS(tpf1_app)

# noinspection PyPep8
from d21_backend.p7_flask_app import routes, auth, template_routes, profiler_routes

from d21_backend.p7_flask_app.api import bp as api_bp

tpf1_app.register_blueprint(api_bp, url_prefix="/api")


@tpf1_app.shell_context_processor
def make_shell_context():
    from d21_backend.config import config
    from d21_backend import tpf
    from d21_backend.p1_utils import domain
    from d21_backend.p1_utils.file_line import File
    from d21_backend.p2_assembly.mac2_data_macro import init_macros
    from d21_backend.p2_assembly.seg8_listing import create_listing_commands, write_tmp_output, LstCmd, create_lxp
    from d21_backend.p2_assembly.seg9_collection import SegLst, get_seg_collection, init_seg_collection
    from d21_backend.p3_db.test_data import TestData
    from d21_backend.p3_db import template_crud
    from d21_backend.p3_db import test_data_get
    from d21_backend.p3_db import test_data_variations
    from d21_backend.p3_db import test_data_elements
    from d21_backend.p3_db import test_results_crud
    from d21_backend.p3_db import template_merge
    from d21_backend.p3_db import template_models
    from d21_backend.p3_db.test_result_model import TestResult
    from d21_backend.p4_execution.ex5_execute import TpfServer
    from d21_backend.p7_flask_app.auth import User, create_user
    from d21_backend.p7_flask_app import routes
    return {
        "TestData": TestData,
        "TestResult": TestResult,
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
        "seg_collection": get_seg_collection(),
        "init_seg_collection": init_seg_collection,
        "init_macros": init_macros,
        "routes": routes,
        "tpf": tpf,
        "template": template_crud,
        "merge": template_merge,
        "test_data_get": test_data_get,
        "templates": template_models,
        "td_variations": test_data_variations,
        "td_elements": test_data_elements,
        "test_results": test_results_crud,
        "domain": domain,
        "create_user": create_user,
    }
