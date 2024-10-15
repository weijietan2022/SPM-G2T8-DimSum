import unittest
import json
from schedule import app  # Adjust the import based on your app structure
from pymongo import MongoClient
from datetime import datetime

class TestGetScheduleAPI(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # Set up a MongoDB client to be used during tests
        self.connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"
        self.client_db = MongoClient(self.connection_string)
        self.userDb = self.client_db['NewAssignment'] 
        self.userCollection = self.userDb['NewAssignment']  
        self.requestsDb = self.client_db['Arrangement']
        self.requestsCollection = self.requestsDb['Arrangement']

        # self.userCollection.insert_one({
        #     "Staff_ID": "test_user",
        #     "Staff_FName": "Test",
        #     "Staff_LName": "User",
        #     "Dept": "HR",
        #     "Position": "Manager",
        #     "Role": 2 
        # })
    
    def tearDown(self):
        # Clean up MongoDB after tests
        self.requestsCollection.delete_many({"Apply_Date": "11 November 2024"})
        self.client_db.close()

    def test_request_is_json(self):
        print("------------Running test_request_is_json-------------")
        response = self.client.post('/api/getSchedule', data='non-json-string', content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Request must be in JSON format"})

    def test_missing_uid_or_date(self):
        print("------------Running test_missing_uid_or_date-------------")
        response = self.client.post('/api/getSchedule', json={"uid": "test_user"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Missing 'uid' or 'date' in request body"})

        response = self.client.post('/api/getSchedule', json={"date": "2024-10-15"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Missing 'uid' or 'date' in request body"})

    def test_invalid_date_format(self):
        print("------------Running test_invalid_date_format-------------")
        response = self.client.post('/api/getSchedule', json={"uid": "test_user", "date": "invalid-date"})
        self.assertEqual(response.status_code, 400)
        # self.assertIn("time data", str(response.json))  # Check for date format error in response
        self.assertEqual(response.json, {"error": "Invalid date format"})

    def test_user_not_found(self):
        print("------------Running test_user_not_found-------------")
        response = self.client.post('/api/getSchedule', json={"uid": "non_existent_user", "date": "2024-10-15"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "User not found"})

    def test_staff_IT_whole_team_wfh(self):
        ## Inserting sample data into the collection
        print("------------Running test_staff_IT_whole_team_wfh-------------")
        i = 17
        while i<45:
            request_id=1000+i
            staff_id=210000+i
            apply_request_data = {
            "Request_ID": request_id,
            "Staff_ID": staff_id,
            "Request_Date": datetime.now(), 
            "Apply_Date": "11 November 2024",
            "Duration": "Full Day",
            "Reason": "i feel like working from home",
            "Manager_ID": 21001,
            "Status": "Pending",
            "File": None
            }

            try:
                self.requestsCollection.insert_one(apply_request_data)
                print("Sample document inserted.")
            except Exception as e:
                print(f"Insert error: {e}")
            i=i+1

        sample_response_data ={
            "inOffice": [],
            "wfh": [
                {
                    "id": 210018,
                    "name": "Manni Devi",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210028,
                    "name": "An Vo",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210017,
                    "name": "Rithe Sok",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210019,
                    "name": "Koh Kok Seng",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210020,
                    "name": "Arifi Saputra",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210021,
                    "name": "Kumar Pillai",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210022,
                    "name": "Narong Phua",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210023,
                    "name": "Thin Ling",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210024,
                    "name": "Vannak Teng",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210025,
                    "name": "Phuon Truong",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210026,
                    "name": "Sri Suon",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210027,
                    "name": "Haing Myat",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210029,
                    "name": "Chin Chin Chen",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210030,
                    "name": "Narah Loo",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210031,
                    "name": "Somachai Kong",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210032,
                    "name": "Rath Khung",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210033,
                    "name": "Chin Nguyen",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210034,
                    "name": "Yee Seng Chong",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210035,
                    "name": "Heng Phalp",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210036,
                    "name": "Sokuntheap Seng",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210037,
                    "name": "Champan Pheap",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210038,
                    "name": "Kahim Harun",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210039,
                    "name": "Halim Sulaiman",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210040,
                    "name": "Trong Nguyen",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210041,
                    "name": "Seng Saon",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210042,
                    "name": "Naron Savoeun",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210043,
                    "name": "Phuc Luon",
                    "status": "Pending",
                    "type": "Full Day"
                },
                {
                    "id": 210044,
                    "name": "Chandara Tithe",
                    "status": "Pending",
                    "type": "Full Day"
                }
            ]
        }
        

        ## Test response from one of the team members
        response = self.client.post('/api/getSchedule', json={"uid": 210017, "date": "2024-11-11"})
        print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, sample_response_data)
        self.assertEqual(len(response.json["wfh"]), 28)

    def test_staff_IT_no_wfh(self):
        print("------------Running test_staff_IT_no_wfh-------------")
        sample_response_data ={
            "inOffice": [
                {
                    "department": "IT",
                    "id": 210018,
                    "name": "Manni Devi",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210028,
                    "name": "An Vo",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210017,
                    "name": "Rithe Sok",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210019,
                    "name": "Koh Kok Seng",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210020,
                    "name": "Arifi Saputra",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210021,
                    "name": "Kumar Pillai",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210022,
                    "name": "Narong Phua",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210023,
                    "name": "Thin Ling",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210024,
                    "name": "Vannak Teng",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210025,
                    "name": "Phuon Truong",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210026,
                    "name": "Sri Suon",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210027,
                    "name": "Haing Myat",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210029,
                    "name": "Chin Chin Chen",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210030,
                    "name": "Narah Loo",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210031,
                    "name": "Somachai Kong",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210032,
                    "name": "Rath Khung",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210033,
                    "name": "Chin Nguyen",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210034,
                    "name": "Yee Seng Chong",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210035,
                    "name": "Heng Phalp",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210036,
                    "name": "Sokuntheap Seng",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210037,
                    "name": "Champan Pheap",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210038,
                    "name": "Kahim Harun",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210039,
                    "name": "Halim Sulaiman",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210040,
                    "name": "Trong Nguyen",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210041,
                    "name": "Seng Saon",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210042,
                    "name": "Naron Savoeun",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210043,
                    "name": "Phuc Luon",
                    "type": "Full Day"
                },
                {
                    "department": "IT",
                    "id": 210044,
                    "name": "Chandara Tithe",
                    "type": "Full Day"
                }
            ],
            "wfh": []
        }

        ## Test response from one of the team members
        response = self.client.post('/api/getSchedule', json={"uid": 210019, "date": "2024-11-11"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, sample_response_data)
        self.assertEqual(len(response.json["inOffice"]), 28)

    def test_managers_sales_no_wfh(self):
        print("------------Running test_managers_sales-------------")
        
        ## Call the api with managers id
        ## Check if the response is correct
        response = self.client.post('/api/getSchedule', json={"uid": 140894, "date": "2024-11-11"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["wfh"]), 0)
        self.assertEqual(len(response.json["inOffice"]),63) #63 because they cannot see directors

    def test_managers_sales_two_wfh(self):
        print("------------Running test_managers_sales_two_wfh-------------")

        ids_for_insertion = [140944,140919]
        for i in ids_for_insertion:
            apply_request_data = {
            "Request_ID": 1000+i,
            "Staff_ID": i,
            "Request_Date": datetime.now(), 
            "Apply_Date": "11 November 2024",
            "Duration": "Full Day",
            "Reason": "i feel like working from home",
            "Manager_ID": 140894,
            "Status": "Pending",
            "File": None
            }

            try:
                self.requestsCollection.insert_one(apply_request_data)
                print("Sample document inserted.")
            except Exception as e:
                print(f"Insert error: {e}")

        response = self.client.post('/api/getSchedule', json={"uid": 140894, "date": "2024-11-11"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["wfh"]), 2)
        self.assertEqual(len(response.json["inOffice"]),61)

    def test_HR_and_directors(self):
        print("------------Running test_HR_and_directors-------------")

        #Get the total number of employees in the db
        total_employees = self.userCollection.count_documents({})
        response = self.client.post('/api/getSchedule', json={"uid": 180001, "date": "2024-11-11"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["wfh"]), 0)
        self.assertEqual(len(response.json["inOffice"]), total_employees)



if __name__ == '__main__':
    unittest.main()
