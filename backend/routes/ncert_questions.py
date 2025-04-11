from flask import Blueprint, render_template, request, jsonify
import requests

bp = Blueprint('ncert_questions', __name__, url_prefix='/ncert-questions')

@bp.route('/')
def index():
    return render_template('components/ncert_questions.html')

# This route directly uses the main app's LLM query API