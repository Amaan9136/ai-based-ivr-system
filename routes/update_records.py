from flask import Blueprint, render_template, request, jsonify
import requests

bp = Blueprint('update_records', __name__, url_prefix='/update-records')

@bp.route('/')
def index():
    return render_template('components/update_records.html')

<<<<<<< HEAD
@bp.route('/api/authenticate', methods=['POST'])
=======
@bp.route('/authenticate', methods=['POST'])
>>>>>>> master
def authenticate():
    data = request.json
    student_id = data.get('student_id', '')
    parent_phone = data.get('parent_phone', '')
    
    # This would normally check against a database
    # For demo, we'll accept any ID that starts with 'STU'
    if student_id.startswith('STU'):
        # Mock student data
        student_data = {
            "id": student_id,
            "name": "Amit Kumar",
            "grade": "7",
            "section": "B",
            "school": "Government High School, Jayanagar",
            "parent_name": "Rajesh Kumar",
            "contact": parent_phone,
            "address": "123, 10th Cross, Jayanagar 4th Block, Bangalore",
            "emergency_contact": "9876543210"
        }
        
        return jsonify({
            'status': 'success',
            'authenticated': True,
            'student': student_data
        })
    else:
        return jsonify({
            'status': 'error',
            'authenticated': False,
            'message': 'Invalid student ID or phone number'
        })

<<<<<<< HEAD
@bp.route('/api/update', methods=['POST'])
=======
@bp.route('/update', methods=['POST'])
>>>>>>> master
def update_record():
    data = request.json
    student_id = data.get('student_id', '')
    field = data.get('field', '')
    value = data.get('value', '')
    
    # In a real app, this would update the database
    # For demo, we'll just acknowledge the update
    
    return jsonify({
        'status': 'success',
        'message': f'Updated {field} for student {student_id}',
        'updated_field': field,
        'new_value': value
    })