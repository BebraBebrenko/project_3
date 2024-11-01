from flask import Blueprint, render_template, request
import requests
bp = Blueprint('forecast', __name__, url_prefix='/forecast')

@bp.post('/forecast')
def forecast_route():
    return None