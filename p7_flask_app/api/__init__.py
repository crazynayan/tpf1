from flask import Blueprint

bp = Blueprint("api", __name__)

from p7_flask_app.api import api9_routes
