import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from autorejection import update_requests, RequestsDB, RejectionDB, UsersDB  # Adjust import if needed

class TestUpdateRequests(unittest.TestCase):

    @patch('autorejection.requests.post')
    def test_update_requests_on_weekday(self, mock_requests_post):
        """Test that requests on a weekday are rejected and notifications are sent."""
        
        # Create mock instances for each database class
        mock_requests_db = MagicMock(RequestsDB)
        mock_rejection_db = MagicMock(RejectionDB)
        mock_users_db = MagicMock(UsersDB)

        # Mock the current date to be a weekday (e.g., Wednesday)
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        next_day = (current_date + timedelta(days=1)).strftime("%d %B %Y")

        # Mock the pending requests in the database
        mock_requests_db.find_pending_requests.return_value = [
            {"Request_ID": "REQ001", "Staff_ID": 123, "Request_Date": "2024-11-15", "Apply_Date": next_day, "Duration": "Full Day", "Status": "Pending"},
        ]
        
        # Mock the rejection operation in MongoDB
        mock_requests_db.reject_requests.return_value = None
        
        # Mock user info
        mock_users_db.find_user_by_id.return_value = {
            "Staff_ID": 123, "Email": "test@example.com", "Staff_FName": "John", "Staff_LName": "Doe"
        }

        # Mock the HTTP post request to send notification
        mock_requests_post.return_value.status_code = 200

        # Run the function
        result = update_requests(mock_requests_db, mock_rejection_db, mock_users_db)

        # Ensure notification was sent
        mock_requests_post.assert_called_once_with("http://localhost:5003/api/sendAutomaticRejectionNotification", json={
            "email": "test@example.com",
            "name": "John Doe",
            "requestId": "REQ001",
            "date": next_day,
            "type": "Full Day"
        })

        # Check result for updated requests
        self.assertEqual(result["requestsUpdated"], 1)
        self.assertEqual(result["totalRequests"], 1)

    @patch('autorejection.requests.post')
    def test_update_requests_on_friday(self, mock_requests_post):
        """Test that requests on Friday are rejected and notifications are sent for Monday."""
        
        # Create mock instances for each database class
        mock_requests_db = MagicMock(RequestsDB)
        mock_rejection_db = MagicMock(RejectionDB)
        mock_users_db = MagicMock(UsersDB)

        # Mock the current date to be a Friday
        friday_date = datetime.now() - timedelta(days=(datetime.now().weekday() - 4) % 7)
        next_monday = (friday_date + timedelta(days=3)).strftime("%d %B %Y")

        # Mock the pending requests in the database
        mock_requests_db.find_pending_requests.return_value = [
            {"Request_ID": "REQ002", "Staff_ID": 124, "Request_Date": "2024-11-18", "Apply_Date": next_monday, "Duration": "Half Day", "Status": "Pending"},
        ]
        
        # Mock the rejection operation in MongoDB
        mock_requests_db.reject_requests.return_value = None
        
        # Mock user info
        mock_users_db.find_user_by_id.return_value = {
            "Staff_ID": 124, "Email": "manager@example.com", "Staff_FName": "Jane", "Staff_LName": "Smith"
        }

        # Mock the HTTP post request to send notification
        mock_requests_post.return_value.status_code = 200

        # Run the function
        result = update_requests(mock_requests_db, mock_rejection_db, mock_users_db)

        # Ensure notification was sent
        mock_requests_post.assert_called_once_with("http://localhost:5003/api/sendAutomaticRejectionNotification", json={
            "email": "manager@example.com",
            "name": "Jane Smith",
            "requestId": "REQ002",
            "date": next_monday,
            "type": "Half Day"
        })

        # Check result for updated requests
        self.assertEqual(result["requestsUpdated"], 1)
        self.assertEqual(result["totalRequests"], 1)

    @patch('autorejection.requests.post')
    def test_no_pending_requests(self, mock_requests_post):
        """Test the case when there are no pending requests to update."""
        
        # Create mock instances for each database class
        mock_requests_db = MagicMock(RequestsDB)
        mock_rejection_db = MagicMock(RejectionDB)
        mock_users_db = MagicMock(UsersDB)

        # Mock no pending requests for the next day
        mock_requests_db.find_pending_requests.return_value = []

        # Run the function
        result = update_requests(mock_requests_db, mock_rejection_db, mock_users_db)

        # Check result for updated requests
        self.assertEqual(result["requestsUpdated"], 0)
        self.assertEqual(result["totalRequests"], 0)


if __name__ == '__main__':
    unittest.main()
