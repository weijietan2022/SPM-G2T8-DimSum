import unittest
from view_request import app  
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
import gridfs

class ViewRequestIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.connection_string = os.getenv("DB_CON_STRING")
        self.client = MongoClient(self.connection_string)
        self.db_arrangement = self.client[os.getenv("DB_ARRANGEMENT")]
        self.collection = self.db_arrangement[os.getenv("COLLECTION_ARRANGEMENT")]
        # Clear the database before starting the tests
        self.collection.delete_many({})
        self.db_new_assignment = self.client[os.getenv("DB_USERS")]
        self.collection_new_assignment = self.db_new_assignment[os.getenv("COLLECTION_USERS")]
        self.db_approval = self.client[os.getenv("DB_APPROVAL")]
        self.collection_approval = self.db_approval[os.getenv("COLLECTION_APPROVAL")]
        # Clear the database before starting the tests
        self.collection_approval.delete_many({})
        self.db_rejection = self.client[os.getenv("DB_REJECTION")]
        self.Reject_Collection = self.db_rejection[os.getenv("COLLECTION_REJECTION")]
        # Clear the database before starting the tests
        self.Reject_Collection.delete_many({})
        self.file_storage = self.client['file_storage']
        self.fs = gridfs.GridFS(self.file_storage)
        self.test_request = {
            "Request_ID": 1,
            "Staff_ID": 140001,
            "Request_Date": datetime.now(),
            "Apply_Date": "11 November 2024",
            "Duration": "Full Day",
            "Reason": "Sick",
            "Manager_ID": 130002,
            "Status": "Pending",
            "File": None
        }
        self.collection.insert_one(self.test_request)

    def tearDown(self):
        ## Clear the database after running the tests
        self.collection.delete_many({})
        self.collection_approval.delete_many({})
        self.Reject_Collection.delete_many({})

        ## Close the database connection
        self.client.close()

    def test_get_requests_based_on_managerID(self):
        newrequest = {
            "Request_ID": 2,
            "Staff_ID": 999999,
            "Request_Date": datetime.now(),
            "Apply_Date": "11 November 2024",
            "Duration": "Full Day",
            "Reason": "Sick",
            "Manager_ID": 999998,
            "Status": "Pending",
            "File": None
        }

        self.collection.insert_one(newrequest)

        response = self.app.get('/api/view-request?dept=CEO&staffId=130002&position=MD&status=All')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.json), len([self.test_request]))


    def test_update_request(self):
        response = self.app.post('/api/update-request', json={"requestId": 1, "status": "Approved", "date": "11 November 2024", "duration": "Full Day"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Request Approved successfully."})

        updated_request = self.collection.find_one({"Request_ID": 1})
        self.assertEqual(updated_request["Status"], "Approved")

    def test_update_request_invalid_requestId(self):
        response = self.app.post('/api/update-request', json={"requestId": 2, "status": "Approved", "date": "11 November 2024", "duration": "Full Day"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Request not found."})

    def test_update_request_invalid_status(self):  
        response = self.app.post('/api/update-request', json={"requestId": 1, "status": "Invalid", "date": "11 November 2024", "duration": "Full Day"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid request data"})

    def test_update_missing_params(self):
        response = self.app.post('/api/update-request', json={"requestId": 1, "status": "Approved", "date": "11 November 2024"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Missing information in request body"})

    def test_approve_request(self):
        ## Change the status of the request to "Approved"
        self.collection.update_one({"Request_ID": 1}, {"$set": {"Status": "Approved"}})

        response = self.app.post('/api/approve-request', json={"requestId": 1, "date": "11 November 2024", "duration": "Full Day"})   
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Request Approved successfully."})

        ## Get the inserted request in approved table
        approved_request = self.collection_approval.find_one({"Request_ID": 1})
        self.assertIsNotNone(approved_request)

    def test_reject_request(self):
        ## Change the status of the request to "Rejected"
        self.collection.update_one({"Request_ID": 1}, {"$set": {"Status": "Rejected"}})

        response = self.app.post('/api/reject-request', 
                                 json={
                                     "Request_ID": 1, "Apply_Date": "11 November 2024", "Duration": "Full Day", "rejectionReason": "Not enough information", "Manager_ID": 130002, "Staff_ID": 140001, "Request_Date": datetime.now()})   
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Rejection submitted successfully"})

        ## Get the inserted request in rejected table
        rejected_request = self.Reject_Collection.find_one({"Request_ID": 1})
        self.assertIsNotNone(rejected_request)




if __name__ == '__main__':
    unittest.main()