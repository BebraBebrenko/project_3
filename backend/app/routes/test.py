from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import requests

bp = Blueprint('test', __name__, url_prefix='/test')

@bp.route('/route', methods=['GET'])
def test_request():
    return 0, 200