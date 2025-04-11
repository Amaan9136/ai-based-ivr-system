from flask import Blueprint, render_template, request, jsonify
import requests

bp = Blueprint('general_questions', __name__, url_prefix='/general-questions')

@bp.route('/')
def index():
    return render_template('components/general_questions.html')

# This route directly uses the main app's LLM query API