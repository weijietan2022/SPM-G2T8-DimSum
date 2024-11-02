import unittest
from unittest.mock import patch, MagicMock
from schedule import app  # Ensure the correct import if the app module is named differently

class TestGetScheduleAPI(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.maxDiff = None

    @patch('schedule.get_user_collection')
    @patch('schedule.get_requests_collection')
    def test_request_is_json(self, mock_get_requests, mock_get_user):
        """Test that the API returns 400 if request is not JSON"""
        response = self.client.post('/api/getSchedule', data='non-json-string', content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Request must be in JSON format"})

    @patch('schedule.get_user_collection')
    @patch('schedule.get_requests_collection')
    def test_missing_uid_or_date(self, mock_get_requests, mock_get_user):
        """Test that the API returns 404 if 'uid' or 'date' are missing"""
        response = self.client.post('/api/getSchedule', json={"uid": "test_user"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Missing 'uid' or 'date' in request body"})

        response = self.client.post('/api/getSchedule', json={"date": "2024-10-15"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Missing 'uid' or 'date' in request body"})

    @patch('schedule.get_user_collection')
    @patch('schedule.get_requests_collection')
    def test_invalid_date_format(self, mock_get_requests, mock_get_user):
        """Test that the API returns 400 for invalid date format"""
        response = self.client.post('/api/getSchedule', json={"uid": "test_user", "date": "invalid-date"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid date format"})

    @patch('schedule.get_user_collection')
    @patch('schedule.get_requests_collection')
    def test_basic_valid_request_role_2_with_team_members(self, mock_get_requests, mock_get_user):
        """Test a valid request for a user with Role 2 and 5 team members in-office"""

        # Define the mock data for the user collection
        team_members = [
            {"Staff_ID": 101, "Staff_FName": "Alice", "Staff_LName": "Smith", "Dept": "IT", "Position": "xsx", "Role": 1, "Reporting_Manager": 100},
            {"Staff_ID": 102, "Staff_FName": "Bob", "Staff_LName": "Johnson", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 101},
            {"Staff_ID": 103, "Staff_FName": "Charlie", "Staff_LName": "Lee", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 101},
            {"Staff_ID": 104, "Staff_FName": "David", "Staff_LName": "Kim", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 101},
            {"Staff_ID": 105, "Staff_FName": "Eva", "Staff_LName": "Brown", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 101},
            {"Staff_ID": 106, "Staff_FName": "Main", "Staff_LName": "User", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 101}
        ]

        # Set up the mock for `find_one` to return the main user only if `Staff_ID` is 106
        mock_user_collection = MagicMock()
        mock_user_collection.find_one.side_effect = lambda query: next((user for user in team_members if user["Staff_ID"] == query.get("Staff_ID")), None)
        
        mock_user_collection.find.side_effect = lambda query: [user for user in team_members if user["Dept"] == query.get("Dept") and user["Position"] == query.get("Position")]
        mock_get_user.return_value = mock_user_collection

        # Mock requests collection to return an empty list of requests (no one is working from home)
        mock_requests_collection = MagicMock()
        mock_requests_collection.find.return_value = []
        mock_get_requests.return_value = mock_requests_collection

        # Expected response: team members should appear in the inOffice list, including the main user
        expected_in_office = [
            {"department": "IT", "id": 106, "name": "Main User", "type": "Full Day"},
            {"department": "IT", "id": 102, "name": "Bob Johnson", "type": "Full Day"},
            {"department": "IT", "id": 103, "name": "Charlie Lee", "type": "Full Day"},
            {"department": "IT", "id": 104, "name": "David Kim", "type": "Full Day"},
            {"department": "IT", "id": 105, "name": "Eva Brown", "type": "Full Day"}
        ]

        # Perform the API request
        response = self.client.post('/api/getSchedule', json={"uid": 106, "date": "2024-11-11"})

        self.assertEqual(response.status_code, 200)

        reponseWfhLength = len(response.json["wfh"])
        expectedWfhLength = 0
        self.assertEqual(reponseWfhLength, expectedWfhLength)

        responseInOfficeLength = len(response.json["inOffice"])
        expectedInOfficeLength = len(expected_in_office)
        self.assertEqual(responseInOfficeLength, expectedInOfficeLength)

    @patch('schedule.get_user_collection')
    @patch('schedule.get_requests_collection')
    def test_basicRole1_director_access(self, mock_get_requests, mock_get_user):
        """Test a valid request for a user with Role 1 (Director), who should see all members and requests in the company"""

        # Define the mock data for the user collection, across multiple departments
        team_members = [
            {"Staff_ID": 101, "Staff_FName": "Alice", "Staff_LName": "Smith", "Dept": "IT", "Position": "Director", "Role": 1, "Reporting_Manager": 100},
            {"Staff_ID": 102, "Staff_FName": "Bob", "Staff_LName": "Johnson", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 101},
            {"Staff_ID": 103, "Staff_FName": "Charlie", "Staff_LName": "Lee", "Dept": "Sales", "Position": "Engineer", "Role": 2, "Reporting_Manager": 101},
            {"Staff_ID": 104, "Staff_FName": "David", "Staff_LName": "Kim", "Dept": "Marketing", "Position": "Manager", "Role": 2, "Reporting_Manager": 101},
            {"Staff_ID": 105, "Staff_FName": "Eva", "Staff_LName": "Brown", "Dept": "HR", "Position": "Specialist", "Role": 2, "Reporting_Manager": 101},
            {"Staff_ID": 106, "Staff_FName": "Main", "Staff_LName": "User", "Dept": "Operations", "Position": "Engineer", "Role": 2, "Reporting_Manager": 101}
        ]

        # Set up the mock for `find_one` to return the director if `Staff_ID` is 101
        mock_user_collection = MagicMock()
        mock_user_collection.find_one.side_effect = lambda query: next((user for user in team_members if user["Staff_ID"] == query.get("Staff_ID")), None)

        # Mock `find` to return all members in the company, as the director has access to all
        mock_user_collection.find.side_effect = lambda query: team_members
        mock_get_user.return_value = mock_user_collection

        # Mock requests collection with specific data
        mock_requests_collection = MagicMock()
        mock_requests_collection.find.return_value = [
            {"Staff_ID": 102, "Duration": "AM", "Status": "Approved", "Apply_Date": "2024-11-11"},
            {"Staff_ID": 103, "Duration": "PM", "Status": "Approved", "Apply_Date": "2024-11-11"},
        ]
        mock_get_requests.return_value = mock_requests_collection

        # Expected response, where the director sees all members, including their WFH and in-office statuses
        expected_wfh = [
            {"id": 102, "name": "Bob Johnson", "status": "Approved", "type": "AM"},
            {"id": 103, "name": "Charlie Lee", "status": "Approved", "type": "PM"},
        ]

        expected_in_office = [
            {"department": "Marketing", "id": 104, "name": "David Kim", "type": "Full Day"},
            {"department": "HR", "id": 105, "name": "Eva Brown", "type": "Full Day"},
            {"department": "Operations", "id": 106, "name": "Main User", "type": "Full Day"},
            {"department": "IT", "id": 101, "name": "Alice Smith", "type": "Full Day"},
            {"department": "Sales", "id": 103, "name": "Charlie Lee", "type": "AM"},
            {"department": "IT", "id": 102, "name": "Bob Johnson", "type": "PM"}
        ]

        # Perform the API request
        response = self.client.post('/api/getSchedule', json={"uid": 101, "date": "2024-11-11"})
        self.assertEqual(response.status_code, 200)

        # Validate the response
        wfhLength = len(response.json["wfh"])  
        expectedWfhLength = len(expected_wfh)
        self.assertEqual(wfhLength, expectedWfhLength)

        inOfficeLength = len(response.json["inOffice"])
        expectedInOfficeLength = len(expected_in_office)
        self.assertEqual(inOfficeLength, expectedInOfficeLength)

    @patch('schedule.get_user_collection')
    @patch('schedule.get_requests_collection')
    def test_manager_role3(self, mock_get_requests, mock_get_user):
        """Test a valid request for a user with Role 3 (Manager), who should see their team members only"""

        # Define the mock data for the user collection
        team_members = [
            {"Staff_ID": 101, "Staff_FName": "Alice", "Staff_LName": "Smith", "Dept": "IT", "Position": "Manager", "Role": 1, "Reporting_Manager": 100},
            {"Staff_ID": 102, "Staff_FName": "Bob", "Staff_LName": "Johnson", "Dept": "IT", "Position": "Engineer", "Role": 3, "Reporting_Manager": 101},
            {"Staff_ID": 103, "Staff_FName": "Charlie", "Staff_LName": "Lee", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 102},
            {"Staff_ID": 104, "Staff_FName": "David", "Staff_LName": "Kim", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 102},
            {"Staff_ID": 105, "Staff_FName": "Eva", "Staff_LName": "Brown", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 102},
            {"Staff_ID": 106, "Staff_FName": "Main", "Staff_LName": "User", "Dept": "IT", "Position": "Engineer", "Role": 2, "Reporting_Manager": 102}
        ]

        # Set up the mock for `find_one` to return the manager if `Staff_ID` is 101
        mock_user_collection = MagicMock()
        mock_user_collection.find_one.side_effect = lambda query: next((user for user in team_members if user["Staff_ID"] == query.get("Staff_ID")), None)

        # Mock `find` to return all members in the IT department except the DIRECTOR
        mock_user_collection.find.side_effect = lambda query: [user for user in team_members if user["Dept"] == query.get("Dept") and user["Position"] != "Manager"]
        mock_get_user.return_value = mock_user_collection

        # Mock requests collection with specific data
        mock_requests_collection = MagicMock()

        # Bob is working from home in the morning, Charlie is working from home in the afternoon
        mock_requests_collection.find.return_value = [
            {"Staff_ID": 102, "Duration": "AM", "Status": "Approved", "Apply_Date": "2024-11-11"},
            {"Staff_ID": 103, "Duration": "Full Day", "Status": "Approved", "Apply_Date": "2024-11-11"},
        ]

        mock_get_requests.return_value = mock_requests_collection

        # Expected response, where the manager sees their team members only
        expected_wfh = [
            {"id": 102, "name": "Bob Johnson", "status": "Approved", "type": "AM"},
            {"id": 103, "name": "Charlie Lee", "status": "Approved", "type": "PM"},
        ]

        expected_in_office = [
            {"department": "IT", "id": 104, "name": "David Kim", "type": "Full Day"},
            {"department": "IT", "id": 105, "name": "Eva Brown", "type": "Full Day"},
            {"department": "IT", "id": 106, "name": "Main User", "type": "Full Day"},
            {"department":"IT", "id":102,"name":"Bob Johnson","type":"PM"},
        ]

        # Perform the API request
        response = self.client.post('/api/getSchedule', json={"uid": 102, "date": "2024-11-11"})

        self.assertEqual(response.status_code, 200)

        # Validate the response
        wfhLength = len(response.json["wfh"])
        expectedWfhLength = len(expected_wfh)
        self.assertEqual(wfhLength, expectedWfhLength)

        inOfficeLength = len(response.json["inOffice"])
        expectedInOfficeLength = len(expected_in_office)
        self.assertEqual(inOfficeLength, expectedInOfficeLength)


if __name__ == '__main__':
    unittest.main()
