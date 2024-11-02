from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import gridfs

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific database
db_arrangement = client['Arrangement']
db = client['Users']
usersdata= db['Users']
staff_ids = usersdata.distinct('Staff_ID')
print(staff_ids)


from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import gridfs

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific databases and collections
db_arrangement = client['Arrangement']
db = client['Users']
usersdata= db['Users']

# Retrieve all unique staff IDs from the collection
staff_ids = usersdata.distinct('Staff_ID')

# Delete all existing WFH requests in the collection, on specific test date to prepare database state for testing
result = db_arrangement['Arrangement'].delete_many({"Apply_Date": "11 November 2024"})

# Insertion of WFH request for all staff, in the form of a document, into the collection 

for staff in staff_ids:
    request_id=1000+staff
    staff_id=staff
    apply_request_data = {
    "Request_ID": request_id,
    "Staff_ID": staff_id,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": "11 November 2024",
    "Duration": "Full Day",
    "Reason": "i feel like working from home",
    "Manager_ID": 1300,
    "Status": "Pending",
    "File": None
    }
    # Insert into the collection
    try:
        db_arrangement['Arrangement'].insert_one(apply_request_data)
        print("Sample document inserted.")
    except Exception as e:
        print(f"Insert error: {e}")