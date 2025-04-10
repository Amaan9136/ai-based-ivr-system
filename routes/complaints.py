from flask import Blueprint, render_template, request, jsonify
import requests
import random
import string

bp = Blueprint('complaints', __name__, url_prefix='/complaints')

@bp.route('/')
def index():
    return render_template('components/complaints.html')

def generate_complaint_id():
    # Generate a random complaint ID
    prefix = "COMP"
    numbers = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{numbers}"

<<<<<<< HEAD
@bp.route('/api/file-complaint', methods=['POST'])
=======
@bp.route('/file-complaint', methods=['POST'])
>>>>>>> master
def file_complaint():
    data = request.json
    complaint_type = data.get('type', '')
    description = data.get('description', '')
    student_id = data.get('student_id', '')
    anonymous = data.get('anonymous', False)
    language = data.get('language', 'english')
    
    # Generate a complaint ID
    complaint_id = generate_complaint_id()
    
    # This would normally save to a database
    # Mock response for demonstration
    
    return jsonify({
        'status': 'success',
        'complaint_id': complaint_id,
        'message': 'Your complaint has been filed successfully',
        'next_steps': 'Your complaint will be reviewed within 24 hours. You can check the status using your complaint ID.'
    })

<<<<<<< HEAD
@bp.route('/api/complaint-types', methods=['GET'])
=======
@bp.route('/complaint-types', methods=['GET'])
>>>>>>> master
def complaint_types():
    # Return available complaint types
    types = [
        {
            "id": "bullying",
            "name": "Bullying",
            "description": "Report incidents of bullying or harassment"
        },
        {
            "id": "absenteeism",
            "name": "Teacher Absenteeism",
            "description": "Report when teachers are frequently absent"
        },
        {
            "id": "discrimination",
            "name": "Discrimination",
            "description": "Report unfair treatment based on gender, caste, religion, etc."
        },
        {
            "id": "misconduct",
            "name": "Teacher Misconduct",
            "description": "Report inappropriate behavior by teachers"
        },
        {
            "id": "infrastructure",
            "name": "Infrastructure Issues",
            "description": "Report problems with school facilities"
        },
        {
            "id": "other",
            "name": "Other Issues",
            "description": "Report any other issues not listed above"
        }
    ]
    
    return jsonify({
        'status': 'success',
        'types': types
    })