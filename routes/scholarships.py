from flask import Blueprint, render_template, request, jsonify
import requests

bp = Blueprint('scholarships', __name__, url_prefix='/scholarships')

@bp.route('/')
def index():
    return render_template('components/scholarships.html')

<<<<<<< HEAD
@bp.route('/api/available-scholarships', methods=['GET'])
=======
@bp.route('/available-scholarships', methods=['GET'])
>>>>>>> master
def available_scholarships():
    # In a real app, this would query a database
    # Mock scholarship data for demonstration
    scholarships = [
        {
            "id": "sch001",
            "name": "National Means-cum-Merit Scholarship",
            "eligibility": "Students of Class 8 with family income less than ₹1,50,000 per annum",
            "amount": "₹12,000 per annum",
            "deadline": "September 30, 2025",
            "documents_required": ["Income Certificate", "Academic Records", "Aadhar Card"]
        },
        {
            "id": "sch002",
            "name": "Pre-Matric Scholarship for SC Students",
            "eligibility": "SC students with family income less than ₹2,50,000 per annum",
            "amount": "₹2,200 per annum",
            "deadline": "October 15, 2025",
            "documents_required": ["Caste Certificate", "Income Certificate", "School Enrollment Proof"]
        },
        {
            "id": "sch003",
            "name": "State Merit Scholarship",
            "eligibility": "Students who scored above 85% in Class 5 or Class 7 examination",
            "amount": "₹5,000 per annum",
            "deadline": "August 31, 2025",
            "documents_required": ["Academic Records", "School Recommendation Letter"]
        }
    ]
    
    return jsonify({
        'status': 'success',
        'scholarships': scholarships
    })

<<<<<<< HEAD
@bp.route('/api/fee-structure', methods=['POST'])
=======
@bp.route('/fee-structure', methods=['POST'])
>>>>>>> master
def fee_structure():
    data = request.json
    school_id = data.get('school_id', '')
    grade = data.get('grade', '')
    
    # This would normally fetch fee information from database
    # Mock fee structure for demonstration
    fee_structure = {
        "tuition_fee": "No tuition fee for government schools",
        "admission_fee": "₹0",
        "examination_fee": "₹0",
        "sports_fee": "₹0",
        "computer_lab_fee": "₹0",
        "note": "Government schools in India do not charge any fees for education up to Class 8 under the Right to Education Act."
    }
    
    return jsonify({
        'status': 'success',
        'fee_structure': fee_structure
    })

<<<<<<< HEAD
@bp.route('/api/apply-scholarship', methods=['POST'])
=======
@bp.route('/apply-scholarship', methods=['POST'])
>>>>>>> master
def apply_scholarship():
    data = request.json
    scholarship_id = data.get('scholarship_id', '')
    student_id = data.get('student_id', '')
    
    # This would normally submit an application to the database
    # Mock response for demonstration
    
    return jsonify({
        'status': 'success',
        'application_id': 'APP' + ''.join([str(ord(c) % 10) for c in scholarship_id + student_id]),
        'message': 'Your scholarship application has been submitted successfully',
        'next_steps': 'You will be notified about the status of your application within 2-3 weeks.'
    })