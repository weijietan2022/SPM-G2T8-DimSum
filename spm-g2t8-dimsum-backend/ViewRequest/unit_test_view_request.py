import unittest
from unittest.mock import patch
from view_request import app, collection  # Adjust import according to actual module name

class UnitTestViewRequest(unittest.TestCase):

    def setUp(self):
        # Configure Flask test client
        self.app = app.test_client()
        self.app.testing = True

    # Test /api/view-request route with 'Pending' status
    @patch('view_request.collection.find')
    def test_get_view_request_pending(self, mock_find):
        # Mock database response for 'Pending' status requests
        mock_find.return_value = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "Staff_ID": 150866,
                "Department": "Engineering",
                "Position": "Manager",
                "Status": "Pending"
            }
        ]
        
        response = self.app.get('/api/view-request', query_string={
            'dept': 'Engineering',
            'staffId': 150866,
            'position': 'Manager',
            'status': 'Pending'
        })
        
        # Verify response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Validate JSON response content
        response_json = response.get_json()
        self.assertEqual(len(response_json), 1)
        self.assertEqual(response_json[0]['Status'], 'Pending')
        self.assertEqual(response_json[0]['Department'], 'Engineering')

    # Test /api/view-request route with 'All' status
    @patch('view_request.collection.find')
    def test_get_view_request_all(self, mock_find):
        # Mock database response for requests of all statuses
        mock_find.return_value = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "Staff_ID": 150866,
                "Department": "Engineering",
                "Position": "Manager",
                "Status": "Pending"
            },
            {
                "_id": "507f1f77bcf86cd799439012",
                "Staff_ID": 150867,
                "Department": "Engineering",
                "Position": "Engineer",
                "Status": "Approved"
            }
        ]
        
        response = self.app.get('/api/view-request', query_string={
            'dept': 'Engineering',
            'staffId': 150866,
            'position': 'Manager',
            'status': 'All'
        })
        
        # Verify response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Validate JSON response content
        response_json = response.get_json()
        self.assertEqual(len(response_json), 2)
        statuses = [req['Status'] for req in response_json]
        self.assertIn('Pending', statuses)
        self.assertIn('Approved', statuses)

    # Test /api/requests route with specified status
    @patch('view_request.collection.find')
    def test_get_requests_with_status(self, mock_find):
        # Mock database response for requests with a specific status
        mock_find.return_value = [
            {
                "_id": "507f1f77bcf86cd799439013",
                "Staff_ID": 150868,
                "Department": "Finance",
                "Position": "Analyst",
                "Status": "Approved"
            }
        ]
        
        response = self.app.get('/api/requests', query_string={'status': 'Approved'})
        
        # Verify response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Validate JSON response content
        response_json = response.get_json()
        self.assertEqual(len(response_json), 1)
        self.assertEqual(response_json[0]['Status'], 'Approved')
        self.assertEqual(response_json[0]['Department'], 'Finance')

    # Test /api/requests route without specified status (return all records)
    @patch('view_request.collection.find')
    def test_get_requests_all(self, mock_find):
        # Mock database response for all requests
        mock_find.return_value = [
            {
                "_id": "507f1f77bcf86cd799439014",
                "Staff_ID": 150869,
                "Department": "HR",
                "Position": "HR Manager",
                "Status": "Pending"
            },
            {
                "_id": "507f1f77bcf86cd799439015",
                "Staff_ID": 150870,
                "Department": "Marketing",
                "Position": "Marketing Specialist",
                "Status": "Approved"
            }
        ]
        
        response = self.app.get('/api/requests')
        
        # Verify response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Validate JSON response content
        response_json = response.get_json()
        self.assertEqual(len(response_json), 2)
        statuses = [req['Status'] for req in response_json]
        self.assertIn('Pending', statuses)
        self.assertIn('Approved', statuses)

    # Test /api/update-request for approving a request
    @patch('view_request.collection.update_one')
    def test_update_request_approve(self, mock_update_one):
        # Mock update_one to return a modified count of 1, indicating success
        mock_update_one.return_value.modified_count = 1
        
        response = self.app.post('/api/update-request', json={
            'requestId': '507f1f77bcf86cd799439011',
            'status': 'Approved'
        })
        
        # Verify response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Validate JSON response content
        response_json = response.get_json()
        self.assertEqual(response_json['message'], 'Request Approved successfully.')

    # Test /api/update-request for rejecting a request
    @patch('view_request.collection.update_one')
    def test_update_request_reject(self, mock_update_one):
        # Mock update_one to return a modified count of 1, indicating success
        mock_update_one.return_value.modified_count = 1
        
        response = self.app.post('/api/update-request', json={
            'requestId': '507f1f77bcf86cd799439011',
            'status': 'Rejected'
        })
        
        # Verify response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Validate JSON response content
        response_json = response.get_json()
        self.assertEqual(response_json['message'], 'Request Rejected successfully.')

    # Test /api/update-request with invalid status
    def test_update_request_invalid_status(self):
        response = self.app.post('/api/update-request', json={
            'requestId': '507f1f77bcf86cd799439011',
            'status': 'InvalidStatus'
        })
        
        # Verify response status code is 400 for invalid data
        self.assertEqual(response.status_code, 400)
        
        # Validate JSON response content
        response_json = response.get_json()
        self.assertEqual(response_json['error'], 'Invalid request data')
    from unittest.mock import patch

# Test /api/approve-request notification handling
@patch('view_request.requests.post')
def test_approve_request_notification_success(self, mock_post):
    mock_post.return_value.status_code = 200
    response = self.app.post('/api/approve-request', json={'requestId': '507f1f77bcf86cd799439011'})
    
    self.assertEqual(response.status_code, 200)
    self.assertIn("Request is sent to the approval database", response.get_json()["Message"])
    mock_post.assert_called_once()

@patch('view_request.requests.post')
def test_approve_request_notification_failure(self, mock_post):
    mock_post.return_value.status_code = 500
    response = self.app.post('/api/approve-request', json={'requestId': '507f1f77bcf86cd799439011'})
    
    self.assertEqual(response.status_code, 500)
    mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
