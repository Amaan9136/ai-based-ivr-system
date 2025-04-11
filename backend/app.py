from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv
from flask_cors import CORS

# Importing and registering blueprints
from routes.nearby_schools import bp as nearby_schools_bp
from routes.complaints import bp as complaints_bp
from routes.scholarships import bp as scholarships_bp
from routes.ncert_questions import bp as ncert_questions_bp
from routes.language_routes import bp as language_bp
from helpers.llm import generate_embeddings, generate_response, find_similarities
from helpers.chroma_helpers import init_all_collections

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
CORS(app) 

# Initialize ChromaDB collections at startup
init_all_collections()

app.register_blueprint(nearby_schools_bp)
app.register_blueprint(complaints_bp)
app.register_blueprint(scholarships_bp)
app.register_blueprint(ncert_questions_bp)
app.register_blueprint(language_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)