from flask import jsonify, request

from p3_db.profiler_methods import run_profiler
from p7_flask_app import tpf1_app
from p7_flask_app.auth import token_auth


@tpf1_app.route("/profiler/run", methods=["POST"])
@token_auth.login_required
def profiler_run():
    return jsonify(run_profiler(request.get_json()))
