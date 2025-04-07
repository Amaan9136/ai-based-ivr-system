from flask import Blueprint, render_template, request, jsonify
import requests
import json

bp = Blueprint('nearby_schools', __name__, url_prefix='/nearby-schools')

@bp.route('/')
def index():
    return render_template('components/nearby_schools.html')

@bp.route('/api/search', methods=['POST'])
def search_schools():
    data = request.json
    location = data.get('location', '')
    language = data.get('language', 'english')
    
    # In a real app, this would query a database of schools
    # For now, we'll simulate it with sample data
    mock_schools = [
        {
            "name": "Government High School, Jayanagar",
            "distance": "1.2 km",
            "address": "10th Main, 4th Block, Jayanagar, Bangalore",
            "admission_status": "Open",
            "grades": "1-10",
            "facilities": ["Computer Lab", "Library", "Playground"]
        },
        {
            "name": "Model Public School, Basavanagudi",
            "distance": "2.5 km",
            "address": "Bull Temple Road, Basavanagudi, Bangalore",
            "admission_status": "Limited seats",
            "grades": "1-12",
            "facilities": ["Science Lab", "Sports Complex", "Digital Classrooms"]
        },
        {
            "name": "Government Primary School, JP Nagar",
            "distance": "3.1 km",
            "address": "5th Phase, JP Nagar, Bangalore",
            "admission_status": "Open",
            "grades": "1-5",
            "facilities": ["Mid-day Meals", "Playground"]
        }
    ]
    
    # Create a context for the LLM
    context = f"Searching for schools near {location}. Found {len(mock_schools)} schools."
    
    return jsonify({
        'status': 'success',
        'schools': mock_schools,
        'context': context
    })

@bp.route('/api/admission-info', methods=['POST'])
def admission_info():
    data = request.json
    school_id = data.get('school_id', '')
    language = data.get('language', 'english')
    
    # This would normally fetch specific admission information
    # Creating mock data for demonstration
    mock_admission_info = {
        "required_documents": ["Birth Certificate", "Address Proof", "Previous School Records"],
        "admission_dates": "June 1 - June 30, 2025",
        "contact_person": "Mrs. Lakshmi (Admission Coordinator)",
        "phone": "080-12345678",
        "fees": "No fees for government schools",
        "process": "1. Submit documents\n2. Verification\n3. Seat allocation"
    }
    
    return jsonify({
        'status': 'success',
        'admission_info': mock_admission_info
    })