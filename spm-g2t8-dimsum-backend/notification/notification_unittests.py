import unittest
from unittest.mock import patch, MagicMock
from notification import app 
from flask import json

class TestNotificationEmails(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('notification.mail.send')  # Mocking the send function of Mail
    def test_send_approval_notification(self, mock_mail_send):
        data = {
            "email": "employee@example.com",
            "name": "John Doe",
            "requestId": "REQ123",
            "date": "2024-11-11",
            "type": "Full Day"
        }
        response = self.app.post('/api/sendApprovalNotification', json=data)

        # Ensure that Mail.send was called once
        mock_mail_send.assert_called_once()

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Email sent successfully"})

    @patch('notification.mail.send')
    def test_send_rejection_notification(self, mock_mail_send):
        data = {
            "email": "employee@example.com",
            "name": "John Doe",
            "requestId": "REQ123",
            "date": "2024-11-11",
            "type": "Half Day"
        }
        response = self.app.post('/api/sendRejectionNotification', json=data)

        mock_mail_send.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Email sent successfully"})

    @patch('notification.mail.send')
    def test_send_request_notification(self, mock_mail_send):
        data = {
            "managerEmail": "manager@example.com",
            "managerName": "Jane Doe",
            "name": "John Doe",
            "requestId": "REQ123",
            "dates": ["2024-11-11", "2024-11-12"],
            "type": "Remote Work"
        }
        response = self.app.post('/api/sendRequestNotification', json=data)

        mock_mail_send.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Email sent successfully"})

    @patch('notification.mail.send')
    def test_send_cancellation_notification(self, mock_mail_send):
        data = {
            "managerEmail": "manager@example.com",
            "managerName": "Jane Doe",
            "name": "John Doe",
            "requestId": "REQ123",
            "date": "2024-11-11",
            "type": "Full Day"
        }
        response = self.app.post('/api/sendCancellationNotification', json=data)

        mock_mail_send.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Email sent successfully"})

    @patch('notification.mail.send')
    def test_send_automatic_rejection_notification(self, mock_mail_send):
        data = {
            "email": "employee@example.com",
            "name": "John Doe",
            "requestId": "REQ123",
            "date": "2024-11-11",
            "type": "Half Day"
        }
        response = self.app.post('/api/sendAutomaticRejectionNotification', json=data)

        mock_mail_send.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Email sent successfully"})

    # Additional test cases for handling invalid requests
    def test_send_approval_notification_invalid_json(self):
        response = self.app.post('/api/sendApprovalNotification', data="Invalid JSON")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Request must be in JSON format"})

    def test_send_approval_notification_missing_fields(self):
        data = {
            "email": "employee@example.com",
            "name": "John Doe"
            # Missing 'requestId', 'date', 'type'
        }
        response = self.app.post('/api/sendApprovalNotification', json=data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Missing information in request body"})


if __name__ == '__main__':
    unittest.main()
