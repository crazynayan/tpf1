from flask import Blueprint

bp = Blueprint("api", __name__)

from flask_app.api import routes
