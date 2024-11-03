## python -m unittest unit_test_login.py
import unittest
from flask import session
from login import app, collection
from unittest.mock import patch

class UnitTestLogin(unittest.TestCase):
    
    # Run before each test
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('login.collection.find_one')
    def test_login_success(self, mock_find_one):
        mock_find_one.return_value = {
            "Staff_ID": 150866,
            "Position": "Senior Engineers",
            "Dept": "Engineering",
            "Staff_FName": "Henry",
            "Staff_LName": "Chan",
            "Reporting_Manager": "Hello Henry!",
            "Role": 2,
            "Reporting_Manager": 151408
        }
        
        # Simulate POST request to /api/login
        response = self.app.post('/api/login', json={
            'email': 'Henry.Chan@allinone.com.sg',
            'password': '150866'
        })
        
        # Verify response status code
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response and validate
        response_json = response.get_json()
        self.assertEqual(response_json['status'], 'success')
        self.assertEqual(response_json['name'], 'Henry Chan')
        self.assertEqual(response_json['position'], 'Senior Engineers')
        self.assertEqual(response_json['dept'], 'Engineering')
        self.assertEqual(response_json['mid'], 151408)
        self.assertEqual(response_json['uid'], 150866)

        # Check session data
        with self.app.session_transaction() as sess:
            self.assertEqual(sess['ID'], 150866)
            self.assertEqual(sess['Position'], 'Senior Engineers')
            self.assertEqual(sess['Department'], 'Engineering')


    # Test for failed login
    # python -m unittest login_test.UnitTestLogin.test_login_fail
    @patch('login.collection.find_one')
    def test_login_fail(self, mock_find_one):
        # Simulate find_one returning None to represent no user found
        mock_find_one.return_value = None
        
        # Simulate POST request to /api/login with incorrect login details
        response = self.app.post('/api/login', json={
            'email': 'wrong.email@allinone.com.sg',
            'password': '123456'
        })
        
        # Verify response status code should be 401 for unauthorized
        self.assertEqual(response.status_code, 401)
        
        # Parse JSON response and validate failure message
        response_json = response.get_json()
        self.assertEqual(response_json['status'], 'fail')
        self.assertEqual(response_json['message'], 'Invalid email or password.')

if __name__ == '__main__':
    unittest.main()
