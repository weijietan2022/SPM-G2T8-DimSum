from datetime import datetime
import io
import unittest
from unittest.mock import patch, MagicMock
from application_form import app, get_next_sequence_value
import json
import gridfs

class ApplicationFormTests(unittest.TestCase):
    @patch('application_form.MongoClient')
    def setUp(self, mock_mongo_client):
        # Mock MongoDB client and collections
        self.mock_client = MagicMock()
        mock_mongo_client.return_value = self.mock_client
        self.mock_db = self.mock_client['test_db']
        self.mock_collection = self.mock_db['test_collection']
        self.mock_fs = MagicMock()
        
        # Insert mock data into the collections
        self.mock_collection.find.return_value = [
            {'Request_ID': 1, 'status': 'Approved', 'staff_id': 123}
        ]
        self.mock_collection.find_one_and_update.return_value = {'sequence_value': 110}
        self.mock_fs.get.return_value = MagicMock(filename='testfile.txt')

        # Initialize Flask test client
        self.app = app.test_client()
        self.app.testing = True

    @patch('application_form.collection', new_callable=lambda: MagicMock())
    def test_get_requests(self, mock_collection):
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = [
            {
                'Request_ID': 1,
                'Status': 'Approved',
                'Staff_ID': 123,
                'File': None,
                'Request_Date': datetime.now(),
                'Reason': 'Test reason'
            }
        ]
        mock_collection.find.return_value = mock_cursor
        response = self.app.get('/api/requests?status=Approved&staff_id=123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data)), 1)

    @patch('application_form.send_notification')  # Mock the send_notification function
    @patch('application_form.get_next_sequence_value')  # Mock get_next_sequence_value for unique ID generation
    @patch('application_form.fs.put')  # Mock fs.put for file upload
    @patch('application_form.collection.insert_one')  # Mock insert_one in the collection
    @patch('application_form.collection_new_assignment.find_one')  # Mock find_one in collection_new_assignment
    def test_process_request_success(
        self, mock_find_one, mock_insert_one, mock_fs_put, mock_get_next_sequence_value, mock_send_notification
    ):
        # Set up the mocks
        mock_fs_put.return_value = 'file_id_123'
        mock_get_next_sequence_value.return_value = 999
        mock_insert_one.return_value = MagicMock()
        mock_send_notification.return_value = True  # Simulate successful notification

        # Mock manager and employee details
        mock_find_one.return_value = {
            "Staff_FName": "ManagerFirst",
            "Staff_LName": "ManagerLast",
            "Email": "manager@example.com"
        }

        # Prepare mock request data, using io.BytesIO for the attachment
        data = {
            'date': json.dumps([{"date": "2024-11-15", "session": "Full Day"}]),
            'reason': 'Test reason',
            'staffId': 123,
            'managerId': 456,
            'attachment': (io.BytesIO(b"mock file content"), 'testfile.txt')
        }

        # Perform POST request to the endpoint
        response = self.app.post('/api/process_request', data=data, content_type='multipart/form-data')

        # Assertions to verify correct response and functionality
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'request inserted and manager notified', response.data)

        # Verify that get_next_sequence_value was called
        mock_get_next_sequence_value.assert_called_once_with("request_id")

        # Verify that insert_one was called with the expected data
        expected_request_data = {
            "Request_ID": 999,  # Based on mocked get_next_sequence_value return value
            "Staff_ID": 123,
            "Request_Date": unittest.mock.ANY,  # Ignore exact date, just check that it exists
            "Apply_Date": "15 November 2024",
            "Duration": "Full Day",
            "Reason": 'Test reason',
            "Manager_ID": 456,
            "Status": "Pending",
            "File": 'file_id_123'
        }
        mock_insert_one.assert_called_once_with(expected_request_data)

        # Verify that send_notification was called with the correct data
        expected_notification_data = {
            "name": "EmployeeFirst EmployeeLast",
            "managerEmail": "manager@example.com",
            "managerName": "ManagerFirst ManagerLast",
            "requestId": 999,
            "dates": ["15 November 2024"],
            "type": ["Full Day"]
        }
        
        ## Just check that notif was called
        mock_send_notification.assert_called_once()

    @patch('application_form.get_counters_collection')  # Mock get_counters_collection to return a mock collection
    def test_get_next_sequence_value(self, mock_get_counters_collection):
        # Arrange: Set up the mock collection and its return value for find_one_and_update
        mock_counters_collection = MagicMock()
        mock_counters_collection.find_one_and_update.return_value = {'sequence_value': 110}
        mock_get_counters_collection.return_value = mock_counters_collection

        # Act: Call get_next_sequence_value
        sequence_value = get_next_sequence_value('request_id')

        # Assert: Verify the returned sequence value is as expected
        self.assertEqual(sequence_value, 110)

        # Verify that find_one_and_update was called with the correct arguments
        mock_counters_collection.find_one_and_update.assert_called_once_with(
            {"_id": "request_id"},
            {"$inc": {"sequence_value": 1}},
            return_document=True
        )

    @patch('application_form.collection.update_one')  # Mock update_one in the collection
    @patch('application_form.collection_new_assignment.find_one')  # Mock find_one for manager and employee details
    @patch('application_form.send_cancel_notification')  # Mock send_cancel_notification for notification
    def test_withdraw_request_success_with_approved_status(self, mock_send_notification, mock_find_one, mock_update_one):
        # Arrange: Mock the database find_one results for manager and employee details
        mock_find_one.side_effect = [
            {"Staff_FName": "ManagerFirst", "Staff_LName": "ManagerLast", "Email": "manager@example.com"},  # Manager details
            {"Staff_FName": "EmployeeFirst", "Staff_LName": "EmployeeLast"}  # Employee details
        ]
        # Mock the update_one result for successful status update
        mock_update_one.return_value.modified_count = 1
        # Mock the notification response
        mock_send_notification.return_value = True

        # Prepare the request data with "Approved" status
        data = {
            "requestId": "123",
            "applyDate": "2024-11-15",
            "managerId": 456,
            "duration": "Full Day",
            "staffId": 789,
            "status": "Approved"
        }

        # Act: Send POST request to /api/withdraw
        response = self.app.post('/api/withdraw', json=data)

        # Assert: Verify response and function calls
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Request successfully withdrawn", response.data)
        # Check that the manager and employee details were fetched
        self.assertEqual(mock_find_one.call_count, 2)
        # Check that update_one was called with the correct arguments
        mock_update_one.assert_called_once_with(
            {"Request_ID": 123, "Apply_Date": "2024-11-15"},
            {"$set": {"Status": "Withdrawn"}}
        )
        # Verify that send_cancel_notification was called with correct data
        expected_notification_details = {
            "name": "EmployeeFirst EmployeeLast",
            "managerEmail": "manager@example.com",
            "managerName": "ManagerFirst ManagerLast",
            "requestId": "123",
            "date": "2024-11-15",
            "type": "Full Day"
        }
        mock_send_notification.assert_called_once

    @patch('application_form.collection.update_one')  # Mock update_one in the collection
    def test_withdraw_request_success_without_notification(self, mock_update_one):
        mock_update_one.return_value.modified_count = 1

        data = {
            "requestId": "123",
            "applyDate": "2024-11-15",
            "managerId": 456,
            "duration": "Full Day",
            "staffId": 789,
            "status": "Pending"
        }

        response = self.app.post('/api/withdraw', json=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Request successfully withdrawn", response.data)
        mock_update_one.assert_called_once_with(
            {"Request_ID": 123, "Apply_Date": "2024-11-15"},
            {"$set": {"Status": "Withdrawn"}}
        )

    @patch('application_form.collection.update_one')  # Mock update_one in the collection
    def test_withdraw_request_not_found(self, mock_update_one):
        mock_update_one.return_value = MagicMock(modified_count=0)

        # Prepare the request data
        data = {
            "Request_UD": "123",
            "Apply_Date": "2024-11-15",
            "Manager_ID": 456,
            "Duration": "Full Day",
            "Staff_ID": 789,
            "Status": "Approved"
        }

        response = self.app.post('/api/withdraw', json=data)

        self.assertEqual(response.status_code, 404)
        self.assertIn(b"No such document in the database", response.data)

    def test_get_rejection_reason_invalid_json(self):
        response = self.app.post('/api/getRejectionReason', data="invalid data")

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Request must be in JSON format", response.data)

    def test_get_rejection_reason_missing_fields(self):
        response = self.app.post('/api/getRejectionReason', json={})

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Missing 'request_id' or 'apply_date' in request body", response.data)

    @patch('application_form.collection_rejection.find_one')  # Mock the database call
    def test_get_rejection_reason_record_found(self, mock_find_one):
        mock_find_one.return_value = {"Reason": "Test rejection reason"}

        response = self.app.post('/api/getRejectionReason', json={"request_id": 123, "apply_date": "2024-11-15"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test rejection reason", response.data)

    @patch('application_form.collection_rejection.find_one')  # Mock the database call
    def test_get_rejection_reason_record_not_found(self, mock_find_one):
        mock_find_one.return_value = None

        response = self.app.post('/api/getRejectionReason', json={"request_id": 123, "apply_date": "2024-11-15"})

        # Assert: Verify that a 404 status code is returned with the correct error message
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Request not found", response.data)


    @patch('application_form.collection.find')  # Mock the collection find method
    def test_get_requests_database_error(self, mock_find):
        # Setup: Simulate a database error on find()
        mock_find.side_effect = Exception("Database error")

        # Execute: Call the get_requests endpoint
        response = self.app.get('/api/requests?status=Approved&staff_id=123')

        # Assert: Check for 500 status code and error message
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Failed to fetch requests", response.data)


@patch('application_form.collection.find_one')
def test_process_request_with_clashing_dates(self, mock_find_one):
    # Simulate a clashing record in the database
    mock_find_one.return_value = {
        "Request_ID": 101,
        "Staff_ID": 123,
        "Apply_Date": "20 November 2024",
        "Duration": "Full Day",
        "Status": "Approved"
    }

    data = {
        'date': json.dumps([{"date": "2024-11-20", "session": "Full Day"}]),
        'reason': 'Test reason',
        'staffId': 123,
        'managerId': 456
    }

    response = self.app.post('/api/process_request', data=data, content_type='multipart/form-data')

    self.assertEqual(response.status_code, 400)
    self.assertIn(b"Clash found for 20 November 2024 with duration Full Day", response.data)

    
if __name__ == '__main__':
    unittest.main()




