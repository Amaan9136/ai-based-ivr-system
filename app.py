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
from helpers.llm import generate_embeddings, generate_response, find_similarities
from helpers.chroma_helpers import init_all_collections

# Initialize ChromaDB collections at startup
init_all_collections()

app.register_blueprint(nearby_schools_bp, url_prefix="/nearby-schools")
app.register_blueprint(update_records_bp, url_prefix="/update-records")
app.register_blueprint(complaints_bp, url_prefix="/complaints")
app.register_blueprint(scholarships_bp, url_prefix="/scholarships")
app.register_blueprint(general_questions_bp, url_prefix="/general-questions")
app.register_blueprint(emergency_bp, url_prefix="/emergency")

@app.route('/')
def index():

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
