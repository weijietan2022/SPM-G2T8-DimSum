import unittest
from notification import app
import os
from dotenv import load_dotenv
from pathlib import Path

class NotificationTest(unittest.TestCase):
    def setUp(self):
        # Load environment variables
        env_path = Path(__file__).resolve().parent / '.env'
        load_dotenv(dotenv_path=env_path)

        # Configure the Flask app explicitly
        app.config['TESTING'] = False  # Set to False to avoid testing mode restrictions
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = os.getenv("EMAIL")
        app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
        
        self.app = app.test_client()

    def test_sendRejectionNotification(self):
        response = self.app.post('/api/sendRejectionNotification', json={
            "email": "titans.aravind@gmail.com",
            "name": "Aravind Saravana",
            "requestId": "1234",
            "date": "30th November 2024",
            "type": "Full Day"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Email sent successfully")

    def test_sendRejectionNotification_missing_email(self):
        response = self.app.post('/api/sendRejectionNotification', json={
            "name": "Aravind Saravana",
            "requestId": "1234",
            "date": "30th November 2024",
            "type": "Full Day"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Missing information in request body")

    def test_sendRejectionNotification_missing_name(self):
        response = self.app.post('/api/sendRejectionNotification', json={
            "email": "titans.aravind@gmail.com",
            "requestId": "1234",
            "date": "30th November 2024",
            "type": "Full Day"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Missing information in request body")

    def test_sendRejectionNotification_missing_requestId(self):
        response = self.app.post('/api/sendRejectionNotification', json={
            "email": "titans.aravind@gmail.com",
            "name": "Aravind Saravana",
            "date": "30th November 2024",
            "type": "Full Day"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Missing information in request body")

    def test_sendRejectionNotification_missing_date(self):
        response = self.app.post('/api/sendRejectionNotification', json={
            "email": "titans.aravind@gmail.com",
            "name": "Aravind Saravana",
            "requestId": "1234",
            "type": "Full Day"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Missing information in request body")

    def test_sendRejectionNotification_missing_type(self):
        response = self.app.post('/api/sendRejectionNotification', json={
            "email": "titans.aravind@gmail.com",
            "name": "Aravind Saravana",
            "requestId": "1234",
            "date": "30th November 2024"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Missing information in request body")

    def test_sendRejectionNotification_not_json(self):
        response = self.app.post('/api/sendRejectionNotification', data={
            "email": "titans.aravind@gmail.com",
            "name": "Aravind Saravana",
            "requestId": "1234",
            "date": "30th November 2024",
            "type": "Full Day"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Request must be in JSON format")


    def test_sendApprovalNotification(self):
        response = self.app.post('/api/sendApprovalNotification', json={
            "email": "titans.aravind@gmail.com",
            "name": "Aravind Saravana",
            "requestId": "1234",
            "date": "30th November 2024",
            "type": "Full Day"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Email sent successfully")

    def test_sendCancellationNotification(self):
        response = self.app.post('/api/sendCancellationNotification', json={
            "managerName": "Aravind Saravana's Boss",
            "name": "Aravind Saravana",
            "requestId": "1234",
            "date": "30th November 2024",
            "type": "Full Day",
            "managerEmail": "titans.aravind@gmail.com"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Email sent successfully")

    def test_sendAutomaticRejectionNotification(self):
        response = self.app.post('/api/sendAutomaticRejectionNotification', json={
            "name": "Aravind Saravana",
            "requestId": "1234",
            "date": "30th November 2024",
            "type": "Full Day",
            "email": "titans.aravind@gmail.com"
        })

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Email sent successfully")

if __name__ == '__main__':
    unittest.main()