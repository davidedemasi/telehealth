import unittest
import json
import os
import sys

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Patient

class PatientAPITestCase(unittest.TestCase):
    """Test case for the patient API."""

    def setUp(self):
        """Set up test client and create test database."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            # Create all tables
            db.create_all()
            
            # Create a test patient
            test_patient = Patient(
                name='Test Patient',
                email='test@example.com',
                phone='123-456-7890'
            )
            db.session.add(test_patient)
            db.session.commit()
        
        # Authentication token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer secret-token-123'
        }

    def tearDown(self):
        """Tear down test database."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_all_patients(self):
        """Test getting all patients."""
        response = self.client.get('/patients', headers=self.headers)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['patients']), 1)
        self.assertEqual(data['patients'][0]['name'], 'Test Patient')
    
    def test_get_patient(self):
        """Test getting a specific patient."""
        response = self.client.get('/patients/1', headers=self.headers)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], 'Test Patient')
        self.assertEqual(data['email'], 'test@example.com')
    
    def test_create_patient(self):
        """Test creating a new patient."""
        patient_data = {
            'name': 'New Patient',
            'email': 'new@example.com',
            'phone': '987-654-3210'
        }
        
        response = self.client.post(
            '/patients',
            data=json.dumps(patient_data),
            headers=self.headers
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['patient']['name'], 'New Patient')
        
        # Verify patient was created in database
        with self.app.app_context():
            patient = Patient.query.filter_by(email='new@example.com').first()
            self.assertIsNotNone(patient)
            self.assertEqual(patient.name, 'New Patient')
    
    def test_update_patient(self):
        """Test updating an existing patient."""
        update_data = {
            'name': 'Updated Name',
            'phone': '555-555-5555'
        }
        
        response = self.client.put(
            '/patients/1',
            data=json.dumps(update_data),
            headers=self.headers
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['patient']['name'], 'Updated Name')
        self.assertEqual(data['patient']['phone'], '555-555-5555')
        
        # Email should remain unchanged
        self.assertEqual(data['patient']['email'], 'test@example.com')
    
    def test_delete_patient(self):
        """Test deleting a patient."""
        response = self.client.delete('/patients/1', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify patient was deleted from database
        with self.app.app_context():
            patient = Patient.query.get(1)
            self.assertIsNone(patient)
    
    def test_missing_token(self):
        """Test accessing endpoint without token."""
        response = self.client.get('/patients')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['message'], 'Authentication token is missing!')
    
    def test_invalid_token(self):
        """Test accessing endpoint with invalid token."""
        headers = {
            'Authorization': 'Bearer invalid-token'
        }
        
        response = self.client.get('/patients', headers=headers)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['message'], 'Invalid authentication token!')

if __name__ == '__main__':
    unittest.main()
