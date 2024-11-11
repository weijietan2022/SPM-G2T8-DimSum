import unittest
from application_form import app
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
import gridfs
import json

class UnitTestApplicationForm(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
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

    def test_get_application_form(self):
        response = self.app.get('/api/requests', query_string={
            'staff_id': 140001
        })

        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(len(response_json), 1)
        self.assertEqual(response_json[0]['Staff_ID'], 140001)
        self.assertEqual(response_json[0]['Manager_ID'], 130002)

    def test_process_wfh_request_success(self):
        response = self.app.post('/api/process_request', 
                                 data={
            "date": json.dumps([{"date": "2025-01-13", "session": "Full Day"}, {"date":"2025-01-14", "session":"Full Day"}]),  # Send cart as JSON string
            "staffId": 140001,
            "managerId": 130002,
            "reason": "My daughter sick",
            "file": (self.fs.put(b'file content', filename='test.txt'), 'test.txt')
        }, content_type='multipart/form-data')  # Set content type to support file uploads

        self.assertEqual(response.status_code, 200)

    def test_process_wfh_request_missing_data(self):
        response = self.app.post('/api/process_request', 
                                 data={
            "date": json.dumps([{"date": "2025-01-13", "session": "Full Day"}, {"date":"2025-01-14", "session":"Full Day"}]),  # Send cart as JSON string
            "staffId": 140001,
            "managerId": 130002,
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 400)

    def test_process_wfh_request_no_date(self):
        response = self.app.post('/api/process_request', 
                                 data={
            "date": json.dumps([]),  # Send cart as JSON string
            "staffId": 140001,
            "managerId": 130002,
            "reason": "My daughter sick"
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 400)

    def test_process_wfh_request_clashing_date(self):
        response = self.app.post('/api/process_request', 
                                 data={
            "date": json.dumps([{"date": "2024-11-11", "session": "Full Day"}, {"date":"2025-01-13", "session":"Full Day"}]),  # Send cart as JSON string
            "staffId": 140001,
            "managerId": 130002,
            "reason": "My daughter sick"
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 400)

    def test_process_wfh_request_invalid_manager(self):
        response = self.app.post('/api/process_request', 
                                 data={
            "date": json.dumps([{"date": "2025-01-13", "session": "Full Day"}, {"date":"2025-01-14", "session":"Full Day"}]),  # Send cart as JSON string
            "staffId": 140001,
            "managerId": 112233,
            "reason": "My daughter sick"
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        ## Check that the message is request added without notification
        response_json = response.get_json()
        self.assertEqual(response_json['message'], 'request inserted without notification')

    def test_withdraw_approvedrequest(self):
        response = self.app.post('/api/withdraw', json={
            'requestId': 1,
            'applyDate': '11 November 2024',
            'duration': 'Full Day',
            'staffId': 140001,
            'status': 'Approved',
            'managerId': 130002
        })

        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['message'], 'Request successfully withdrawn')

    def test_withdraw_approved_request_invalid_requestId(self):
        response = self.app.post('/api/withdraw', json={
            'requestId': 2,
            'applyDate': '11 November 2024',
            'duration': 'Full Day',
            'staffId': 140001,
            'status': 'Approved',
            'managerId': 130002
        })

        self.assertEqual(response.status_code, 404)
        response_json = response.get_json()
        self.assertEqual(response_json['message'], 'Failed to update database')

    def test_withdraw_approved_pending_invalid_requestId(self):
        response = self.app.post('/api/withdraw', json={
            'requestId': 2,
            'applyDate': '11 November 2024',
            'duration': 'Full Day',
            'staffId': 140001,
            'status': 'Pending',
            'managerId': 130002
        })

        self.assertEqual(response.status_code, 404)
        response_json = response.get_json()
        self.assertEqual(response_json['message'], 'Request not found or already withdrawn')

    def test_withdraw_pendingrequest(self):
        response = self.app.post('/api/withdraw', json={
            'requestId': 1,
            'applyDate': '11 November 2024',
            'duration': 'Full Day',
            'staffId': 140001,
            'status': 'Pending',
            'managerId': 130002
        })

        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['message'], 'Request successfully withdrawn')

    def test_rejection_reason_success(self):
        ## insert rejection in rejection db
        self.Reject_Collection.insert_one({
            'Request_ID': 1,
            'Staff_ID': 140001,
            'Request_Date': datetime.now(),
            'Apply_Date': '11 November 2024',
            'Duration': 'Full Day',
            'Manager_ID': 130002,
            'Reason': 'I dont like you',
            'Reject_Date_Time': datetime.now()
        })

        response = self.app.post('/api/getRejectionReason', json={
            'request_id': 1,
            'apply_date': '11 November 2024',
        })

        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['reason'], 'I dont like you')

    def test_rejection_reason_invalid_requestId(self):
        response = self.app.post('/api/getRejectionReason', json={
            'request_id': 2,
            'apply_date': '11 November 2024',
        })

        self.assertEqual(response.status_code, 404)
        response_json = response.get_json()
        self.assertEqual(response_json['error'], 'Request not found')

    def test_rejection_reason_missing_data(self):
        response = self.app.post('/api/getRejectionReason', json={
            'request_id': 1,
        })

        self.assertEqual(response.status_code, 400)
        response_json = response.get_json()
        self.assertEqual(response_json['error'], "Missing 'request_id' or 'apply_date' in request body")

if __name__ == '__main__':
    unittest.main()


