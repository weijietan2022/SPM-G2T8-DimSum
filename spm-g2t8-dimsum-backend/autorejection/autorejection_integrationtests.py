from datetime import datetime, timedelta
import unittest
import os
from dotenv import load_dotenv
from pathlib import Path
import pymongo
from autorejection import update_requests, RequestsDB, RejectionDB, UsersDB  # Adjust imports as needed

class TestAutoRejectionModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load environment variables for test database
        env_path = Path(__file__).resolve().parent / '.env.test'
        load_dotenv(dotenv_path=env_path)

        # Initialize MongoDB connection and databases
        cls.connection_string = os.getenv('CONNECTION_STRING')
        cls.client = pymongo.MongoClient(cls.connection_string)
        cls.requests_db = RequestsDB()
        cls.rejection_db = RejectionDB()
        cls.users_db = UsersDB()

    def setUp(self):
        # Clear both the requests and rejection collections before each test
        self.requests_db.collection.delete_many({})
        self.rejection_db.collection.delete_many({})

        ## Calculate the next working day and the day after that
        # Get the current day of the week
        current_day = datetime.now().weekday()
        # Calculate the number of days to add to reach the next working day
        days_to_add = 1 if current_day < 4 else 4 - current_day
        # Calculate the next working day
        self.next_working_day = datetime.now() + timedelta(days=days_to_add)
        # Calculate the day after the next working day, if it is a Friday, add 3 days, else add 1 day
        self.day_after_next = self.next_working_day + timedelta(days=3 if self.next_working_day.weekday() == 4 else 1)
        # Convert them to %d %b %Y format - should be like 04 November 2024. November should be the full month name
        self.next_working_day_str = self.next_working_day.strftime("%d %B %Y")
        self.day_after_next_str = self.day_after_next.strftime("%d %B %Y")
        

        # Add mock data to the requests collection
        self.requests_db.collection.insert_many([
            {
                "Request_ID": 1,
                "Staff_ID": 999999,
                "Request_Date": datetime.now(),
                "Apply_Date": self.next_working_day_str,
                "Duration": "Full Day",
                "Manager_ID": 999998,
                "Reason": "No reason",
                "Status": "Pending",
                "File": None
            },
            {
                "Request_ID": 2,
                "Staff_ID": 999999,
                "Request_Date": datetime.now(),
                "Apply_Date": self.day_after_next_str,
                "Duration": "Full Day",
                "Manager_ID": 999998,
                "Reason": "No reason",
                "Status": "Pending",
                "File": None
            },
        ])

    def tearDown(self):
        # Clear collections after each test to ensure isolation
        # self.requests_db.collection.delete_many({})
        # self.rejection_db.collection.delete_many({})
        pass

    def test_update_requests(self):
        # Run the function
        result = update_requests(self.requests_db, self.rejection_db, self.users_db)
        
        # Validate results in result data
        total_requests = result['totalRequests']
        updated_requests = result['requestsUpdated']
        self.assertEqual(updated_requests, 1)
        self.assertEqual(total_requests, 1)

        # Validate the number of requests in the rejection collection matches updated requests
        rejection_count = self.rejection_db.collection.count_documents({})
        self.assertEqual(rejection_count, updated_requests)

        # Verify that the rejection collection has specific records with the expected fields
        rejected_request = self.rejection_db.collection.find_one({"Request_ID": 1})
        self.assertIsNotNone(rejected_request)
        self.assertEqual(rejected_request["Reason"], "Automated Rejection - The request was not approved or rejected prior to 24 hours before the request date.")
        self.assertIn("Reject_Date_Time", rejected_request)  # Check that rejection timestamp is recorded

        # Verify that the status of the rejected request in the requests collection is updated
        updated_request = self.requests_db.collection.find_one({"Request_ID": 1})
        self.assertIsNotNone(updated_request)
        self.assertEqual(updated_request["Status"], "Rejected")

if __name__ == '__main__':
    unittest.main()
