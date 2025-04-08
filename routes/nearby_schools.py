from flask import Blueprint, render_template, request, jsonify
from helpers.chatters import chat_with_history

bp = Blueprint('nearby_schools', __name__, url_prefix='/nearby-schools')

@bp.route('/')
def index():
    return render_template('components/nearby_schools.html')

@bp.route('/api/nearby_school_finder', methods=['POST'])
def chatbot_response():
    data = request.json
    prompt = data.get('prompt', '')
    old_summary = data.get('old_response_summary', '')

    if not prompt.strip():
        return jsonify({'status': 'error', 'response': 'Please provide a question.'}), 400

    try:
        chat_result = chat_with_history(prompt=prompt, old_summary=old_summary)
        return jsonify({
            'status': 'success',
            'response': chat_result['new_response'],
            'old_response_summary': chat_result['old_response_summary']
        })
    except Exception as e:
        print(f"[LLM Error] {e}")
        return jsonify({'status': 'error', 'response': 'Something went wrong while generating the response.'}), 500
