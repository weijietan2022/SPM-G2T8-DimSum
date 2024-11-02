from datetime import datetime
import unittest
from autorejection import app
import os
from dotenv import load_dotenv
from pathlib import Path
import pymongo

class TestAutoRejectionModule(unittest.TestCase):
    def setUp(self):
        env_path = Path(__file__).resolve().parent / '.env'
        load_dotenv(dotenv_path=env_path)

        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        self.connection_string = os.getenv('CONNECTION_STRING')
        client = pymongo.MongoClient(self.connection_string)
        self.requests_db = client[os.getenv("DB_ARRANGEMENT")]
        self.requests_collection = self.requests_db[os.getenv("COLLECTION_ARRANGEMENT")]
        self.rejection_db = client[os.getenv("DB_REJECTION")]
        self.rejection_collection = self.rejection_db[os.getenv("COLLECTION_REJECTION")]
        self.users_db = client[os.getenv("DB_USERS")]
        self.users_collection = self.users_db[os.getenv("COLLECTION_USERS")]

        # Clear both the requests and rejection collections

        self.requests_collection.delete_many({})
        self.rejection_collection.delete_many({})

        # Add in 2 requests to the requests collection
        self.requests_collection.insert_many([
            {
                "Request_ID": 1,
                "Staff_ID": 999999,
                "Request_Date": datetime.now(),
                "Apply_Date": "04 November 2024",
                "Duration": "Full Day",
                "Manager_ID": 999998,
                "Reason": "No reason",
                "Status": "Pending",
                "File": ""
            },
            {
                "Request_ID": 2,
                "Staff_ID": 999999,
                "Request_Date": datetime.now(),
                "Apply_Date": "05 November 2024",
                "Duration": "Full Day",
                "Manager_ID": 999998,
                "Reason": "No reason",
                "Status": "Pending",
                "File": ""
            },
        ])
        
        
    def test_update_requests(self):
        response = self.client.post('/update_requests')
        ## Response data will have 2 fields - totalRequests and updatedRequests
        data = response.get_json()
        totalRequests = data['totalRequests']
        updatedRequests = data['updatedRequests']
        self.assertEqual(updatedRequests, 1)
        self.assertEqual(totalRequests, 1)

        ## Get the number of requests in the rejection collection
        rejection_count = self.rejection_collection.count_documents({})
        self.assertEqual(rejection_count, updatedRequests)




