from pymongo import MongoClient
from datetime import datetime

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific database
db_arrangement = client['Arrangement']

# Insert a sample document into the collection using datetime objects
apply_request_data_1 = {
    "Request_ID": 1,
    "Staff_ID": 1001,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": datetime(2024, 10, 1),
    "Duration": "AM",
    "Manager_ID": 5001,
    "Status": "Pending",
}

# Insert into the collection
try:
    db_arrangement['Arrangement'].insert_one(apply_request_data_1)
    print("Sample document inserted.")
except Exception as e:
    print(f"Insert error: {e}")


# Insert a sample document into the collection using datetime objects
apply_request_data_2 = {
    "Request_ID": 1,
    "Staff_ID": 1001,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": datetime(2024, 10, 2),
    "Duration": "AM",
    "Manager_ID": 5001,
    "Status": "Pending",
}

# Insert into the collection
try:
    db_arrangement['Arrangement'].insert_one(apply_request_data_2)
    print("Sample document inserted.")
except Exception as e:
    print(f"Insert error: {e}")



#######################################################################################
#######################################################################################
#######################################################################################



# Access the specific database
db_rejected = client['Rejected']

# Insert a sample document into the collection using datetime objects
rejected_data = {
    "Request_ID": 1,
    "Staff_ID": 1001,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": datetime(2024, 10, 1),
    "Duration": "AM",
    "Manager_ID": 5001,
    "Reason": "I need you to be in office for f2f meeting",
}

# Insert into the collection
try:
    db_rejected['Rejected'].insert_one(rejected_data)
    print("Sample document inserted.")
except Exception as e:
    print(f"Insert error: {e}")



#######################################################################################
#######################################################################################
#######################################################################################



# Function to get the next sequence value
def get_next_sequence_value(sequence_name):
    # Find and update the counter for the given sequence name
    result = db['counters'].find_one_and_update(
        {"_id": sequence_name},   # The document where _id = sequence_name
        {"$inc": {"sequence_value": 1}},  # Increment the sequence_value by 1
        return_document=True     # Return the updated document after the increment
    )
    return result['sequence_value']  # Return the incremented sequence_value

# Example usage: Inserting a new Request_ID
request_id = get_next_sequence_value("request_id")
print(f"Next Request_ID: {request_id}")