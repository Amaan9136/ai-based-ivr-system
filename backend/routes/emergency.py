from flask import Blueprint, render_template, request, jsonify
import requests
import random
import string

bp = Blueprint('emergency', __name__, url_prefix='/emergency')

@bp.route('/')
def index():
    return render_template('components/emergency.html')

def generate_case_id():
    # Generate a random case ID for emergency reports
    prefix = "EMG"
    numbers = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{numbers}"

@bp.route('/report-emergency', methods=['POST'])
def report_emergency():
    data = request.json
    emergency_type = data.get('type', '')
    description = data.get('description', '')
    location = data.get('location', '')
    contact = data.get('contact', '')
    anonymous = data.get('anonymous', False)
    
    # Generate a case ID
    case_id = generate_case_id()
    
    # This would normally save to a database and alert appropriate personnel
    # Mock response for demonstration
    
    emergency_response = {
        'status': 'success',
        'case_id': case_id,
        'message': 'Your emergency report has been submitted and will be addressed immediately',
        'priority': 'High',
        'contact_info': 'Emergency Response Team: 1800-XXX-XXXX'
    }
    
    if emergency_type.lower() in ['abuse', 'violence', 'assault']:
        emergency_response['additional_info'] = 'For immediate assistance, please also contact the Child Helpline at 1098'
    
    return jsonify(emergency_response)

@bp.route('/emergency-types', methods=['GET'])
def emergency_types():
    # Return available emergency report types
    types = [
        {
            "id": "abuse",
            "name": "Child Abuse",
            "description": "Report incidents of physical, emotional, or sexual abuse"
        },
        {
            "id": "violence",
            "name": "Violence in School",
            "description": "Report violent incidents in or around school premises"
        },
        {
            "id": "health",
            "name": "Health Emergency",
            "description": "Report health-related emergencies requiring immediate attention"
        },
        {
            "id": "safety",
            "name": "Safety Hazard",
            "description": "Report dangerous conditions or safety hazards in school"
        },
        {
            "id": "other",
            "name": "Other Emergency",
            "description": "Report any other emergency situations"
        }
    ]
    
    return jsonify({
        'status': 'success',
        'types': types
    })