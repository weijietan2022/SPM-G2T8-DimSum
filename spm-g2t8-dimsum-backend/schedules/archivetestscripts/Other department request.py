from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import gridfs

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific database
db_arrangement = client['Arrangement']

result = db_arrangement['Arrangement'].delete_many({"Apply_Date": "11 November 2024"})
apply_request_data_1 = {
    "Request_ID": 100001,
    "Staff_ID": 150566,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": "11 October 2024",
    "Duration": "AM",
    "Reason": "testing data number 2",
    "Manager_ID": 151408,
    "Status": "Pending",
    "File": None
}

# Insert into the collection
try:
    db_arrangement['Arrangement'].insert_one(apply_request_data_1)
    print("Sample document inserted.")
except Exception as e:
    print(f"Insert error: {e}")
