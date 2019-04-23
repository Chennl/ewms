from flask import Blueprint

bp = Blueprint('warehouese',__name__)

from app.warehouse import routes