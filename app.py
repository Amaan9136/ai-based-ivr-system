from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Importing and registering blueprints
from routes.nearby_schools import bp as nearby_schools_bp
from routes.update_records import bp as update_records_bp
from routes.complaints import bp as complaints_bp
from routes.scholarships import bp as scholarships_bp
from routes.general_questions import bp as general_questions_bp
from routes.emergency import bp as emergency_bp

app.register_blueprint(nearby_schools_bp, url_prefix="/nearby-schools")
app.register_blueprint(update_records_bp, url_prefix="/update-records")
app.register_blueprint(complaints_bp, url_prefix="/complaints")
app.register_blueprint(scholarships_bp, url_prefix="/scholarships")
app.register_blueprint(general_questions_bp, url_prefix="/general-questions")
app.register_blueprint(emergency_bp, url_prefix="/emergency")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/set-language', methods=['POST'])
def set_language():
    language = request.json.get('language', 'english')
    # In real use-case: store this in session or user prefs
    return jsonify({'status': 'success', 'language': language})

@app.route('/api/llm-query', methods=['POST'])
def llm_query():
    data = request.json
    user_input = data.get('query', '')
    context = data.get('context', '')
    language = data.get('language', 'english')

    prompt = f"Language: {language}\nContext: {context}\nUser: {user_input}\nAssistant:"

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',  # Ensure you’re using the correct endpoint
            json={
                'model': 'llama3.2:latest',
                'prompt': prompt,
                'stream': False
            }
        )

        if response.ok:
            result = response.json()
            return jsonify({
                'status': 'success',
                'response': result.get('response', 'No response generated.')
            })

        return jsonify({
            'status': 'error',
            'message': f"Ollama API error: {response.status_code} {response.text}"
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
