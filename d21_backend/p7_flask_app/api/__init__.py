from flask import Blueprint

bp = Blueprint("api", __name__)

from d21_backend.p7_flask_app.api import api9_routes
