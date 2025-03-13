from flask import Flask, request, jsonify
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import db, Patient
from auth import token_required
from tasks import send_notification

# Initialize Flask app
app = Flask(__name__)

# Configure database from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Error handler for general exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for server errors."""
    return jsonify(error=str(e)), 500

# Create a new patient
@app.route('/patients', methods=['POST'])
@token_required
def create_patient():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Check if patient with this email already exists
    existing_patient = Patient.query.filter_by(email=data['email']).first()
    if existing_patient:
        return jsonify({'message': 'Patient with this email already exists'}), 409
    
    # Create new patient
    new_patient = Patient(
        name=data['name'],
        email=data['email'],
        phone=data['phone']
    )
    
    # Add to database
    db.session.add(new_patient)
    db.session.commit()
    
    # Trigger background task
    send_notification.delay(
        patient_id=new_patient.id,
        patient_name=new_patient.name,
        patient_contact=new_patient.email,
        notification_type='email'
    )
    
    return jsonify({
        'message': 'Patient created successfully',
        'patient': new_patient.to_dict()
    }), 201

# Get patient by ID
@app.route('/patients/<int:patient_id>', methods=['GET'])
@token_required
def get_patient(patient_id):
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    
    return jsonify(patient.to_dict()), 200

# Update patient details
@app.route('/patients/<int:patient_id>', methods=['PUT'])
@token_required
def update_patient(patient_id):
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    
    data = request.get_json()
    
    # Update patient fields if provided
    if 'name' in data:
        patient.name = data['name']
    if 'email' in data:
        # Check if another patient already has this email
        existing_patient = Patient.query.filter_by(email=data['email']).first()
        if existing_patient and existing_patient.id != patient_id:
            return jsonify({'message': 'Another patient with this email already exists'}), 409
        patient.email = data['email']
    if 'phone' in data:
        patient.phone = data['phone']
    
    db.session.commit()
    
    # Trigger background task
    send_notification.delay(
        patient_id=patient.id,
        patient_name=patient.name,
        patient_contact=patient.email,
        notification_type='email'
    )
    
    return jsonify({
        'message': 'Patient updated successfully',
        'patient': patient.to_dict()
    }), 200

# Delete patient
@app.route('/patients/<int:patient_id>', methods=['DELETE'])
@token_required
def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    
    db.session.delete(patient)
    db.session.commit()
    
    return jsonify({'message': 'Patient deleted successfully'}), 200

# Get all patients
@app.route('/patients', methods=['GET'])
@token_required
def get_all_patients():
    # Optional pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    patients = Patient.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': patients.total,
        'pages': patients.pages,
        'current_page': patients.page,
        'patients': [patient.to_dict() for patient in patients.items]
    }), 200

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True)