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

# Access the specific database
db_approval = client['Approval']

# Delete all existing WFH requests in the collection, on specific test date to prepare database state for testing
result = db_approval['Approval'].delete_many({"Apply_Date": "11 November 2024"})

# Insertion of sample WFH request, in the form of a document, into the collection 
apply_request_data_1 = {
    "Request_ID": 1002,
    "Staff_ID": 210029,
    "Request_Date": datetime.now(),  
    "Apply_Date": "11 November 2024",
    "Duration": "Full Day",
    "Reason": "i feel like working from home",
    "Manager_ID": 210001,
    "Status": "Pending",
    "File": None
}

# Insert into the collection
try:
    db_arrangement['Arrangement'].insert_one(apply_request_data_1)
    print("Sample document inserted.")
except Exception as e:
    print(f"Insert error: {e}")


# Insertion of sample WFH request, in the form of a document, into the collection 
apply_request_data_2 = {
    "Request_ID": 1004,
    "Staff_ID": 210042,
    "Request_Date": datetime.now(),  
    "Apply_Date": "11 November 2024",
    "Duration": "PM",
    "Reason": "i feel like working from home",
    "Manager_ID": 210001,
    "Status": "Pending",
    "File": None
}

# Insert into the collection
try:
    db_arrangement['Arrangement'].insert_one(apply_request_data_2)
    print("Sample document inserted.")
except Exception as e:
    print(f"Insert error: {e}")
    
# Insertion of sample WFH request, in the form of a document, into the collection 
apply_request_data_3 = {
    "Request_ID": 1053,
    "Staff_ID": 210043,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": "11 November 2024",
    "Duration": "AM",
    "Reason": "i feel like working from home",
    "Manager_ID": 210001,
    "Status": "Pending",
    "File": None
}

# Insert into the collection
try:
    db_arrangement['Arrangement'].insert_one(apply_request_data_3)
    print("Sample document inserted.")
except Exception as e:
    print(f"Insert error: {e}")
    
# Insertion of sample WFH request, in the form of a document, into the collection 
apply_request_data_4 = {
    "Request_ID": 1063,
    "Staff_ID": 210041,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": "11 November 2024",
    "Duration": "AM",
    "Reason": "i feel like working from home",
    "Manager_ID": 210001,
    "Status": "Pending",
    "File": None
}

# Insert into the collection
try:
    db_arrangement['Arrangement'].insert_one(apply_request_data_4)
    print("Sample document inserted.")
except Exception as e:
    print(f"Insert error: {e}")