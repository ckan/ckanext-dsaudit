from flask import Blueprint
from flask.views import MethodView

from ckan.plugins import toolkit as tk

dsaudit = Blueprint('dsaudit', __name__)

