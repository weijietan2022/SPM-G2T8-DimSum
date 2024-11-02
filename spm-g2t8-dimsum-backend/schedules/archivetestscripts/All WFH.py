from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import gridfs

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific database
db_arrangement = client['Arrangement']

# Delete all existing WFH requests in the collection, on specific test date to prepare database state for testing
result = db_arrangement['Arrangement'].delete_many({"Apply_Date": "11 November 2024"})

# Insertion of WFH requests for the entire department

i=17
while i<45:
    request_id=1000+i
    staff_id=210000+i
    apply_request_data = {
    "Request_ID": request_id,
    "Staff_ID": staff_id,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": "11 November 2024",
    "Duration": "Full Day",
    "Reason": "i feel like working from home",
    "Manager_ID": 21001,
    "Status": "Pending",
    "File": None
    }

# Insert into the collection
    try:
        db_arrangement['Arrangement'].insert_one(apply_request_data)
        print("Sample document inserted.")
    except Exception as e:
        print(f"Insert error: {e}")
    i=i+1

    

