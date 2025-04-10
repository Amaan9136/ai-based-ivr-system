from flask import Blueprint, request, jsonify, session

bp = Blueprint('language', __name__, url_prefix='/language')

@bp.route('/set-language', methods=['POST'])
def set_language():
    data = request.get_json()
    language = data.get('language')
    ALLOWED_LANGUAGES = ["english", "kannada", "hindi"]

    if language and language in ALLOWED_LANGUAGES:
        session['selected_language'] = language
        return jsonify({'status': 'success', 'message': f'Language set to {language}'})
    elif language:
        return jsonify({'status': 'error', 'message': f"Unsupported language. Allowed: {', '.join(ALLOWED_LANGUAGES)}"}), 400
    else:
        return jsonify({'status': 'error', 'message': 'No language provided'}), 400

@bp.route('/get-language', methods=['GET'])
def get_language():
    language = session.get('selected_language', 'english')
    return jsonify({'language': language})
