from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import gridfs

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

db_arrangement = client['NewArrangement']

# Function to get the next sequence value
# def get_next_sequence_value(sequence_name):
#     # Access the correct counters collection
#     counters_collection = client['NewArrangement']['counters']  # Replace with the actual database name

#     # Find and update the counter for the given sequence name
#     result = counters_collection.find_one_and_update(
#         {"_id": sequence_name},   # The document where _id = sequence_name
#         {"$inc": {"sequence_value": 1}},  # Increment the sequence_value by 1
#         return_document=True     # Return the updated document after the increment
#     )

#     if result:
#         return result['sequence_value']  # Return the incremented sequence_value
#     else:
#         raise Exception(f"Sequence {sequence_name} not found.")

# # Example usage: Generating unique Request_ID
# request_id_1 = get_next_sequence_value("request_id")
# request_id_2 = get_next_sequence_value("request_id")

# Insert a sample document into the collection using datetime objects (with Department)
apply_request_data_1 = {
    "Request_ID": 5,  # Use the generated request_id
    "Staff_ID": 1001,
    "Request_Date": datetime.now(),  # Proper datetime object
    "Apply_Date": "10 October 2024",
    "Duration": "AM",
    "Reason": "i feel like working from home, no mood",
    "Manager_ID": 5001,
    "Status": "Pending",
    "File": None,
    "Department": "Sales"  # New Department field
}

# Insert into the collection
try:
    db_arrangement['Arrangement'].insert_one(apply_request_data_1)
    print("Sample document 1 inserted.")
except Exception as e:
    print(f"Insert error: {e}")

# Insert another sample document into the collection using datetime objects (with Department)
# apply_request_data_2 = {
#     "Request_ID": 2,  # Use the generated request_id
#     "Staff_ID": 1001,
#     "Request_Date": datetime.now(),  # Proper datetime object
#     "Apply_Date": "11 October 2024",
#     "Duration": "AM",
#     "Reason": "testing data number 2",
#     "Manager_ID": 5001,
#     "Status": "Pending",
#     "File": ObjectId('60f7e6af1c4b3a7c9c8b4567'),
#     "Department": "Engineering"  # New Department field
# }

# # Insert into the collection
# try:
#     db_arrangement['Arrangement'].insert_one(apply_request_data_2)
#     print("Sample document 2 inserted.")
# except Exception as e:
#     print(f"Insert error: {e}")

# #######################################################################################

# # Access the Rejected database
# db_rejected = client['Rejected']

# # Insert a sample document into the collection using datetime objects (with Department)
# rejected_data = {
#     "Request_ID": 3,  # Get a new request_id for the rejected document
#     "Staff_ID": 1001,
#     "Request_Date": datetime.now(),  # Proper datetime object
#     "Apply_Date": datetime(2024, 10, 1),
#     "Duration": "AM",
#     "Manager_ID": 5001,
#     "Reason": "I need you to be in office for f2f meeting",
#     "Reject_Date_Time": datetime.now(),  # Fixed field name
#     "Department": "HR"  # New Department field
# }

# # Insert into the collection
# try:
#     db_rejected['Rejected'].insert_one(rejected_data)
#     print("Rejected document inserted.")
# except Exception as e:
#     print(f"Insert error: {e}")


#######################################################################################
#######################################################################################
#######################################################################################



# # Function to get the next sequence value
# def get_next_sequence_value(sequence_name):
#     # Find and update the counter for the given sequence name
#     result = client['NewArrangement']['counters'].find_one_and_update(
#         {"_id": sequence_name},   # The document where _id = sequence_name
#         {"$inc": {"sequence_value": 1}},  # Increment the sequence_value by 1
#         return_document=True     # Return the updated document after the increment
#     )
#     return result['sequence_value']  # Return the incremented sequence_value

# # Example usage: Inserting a new Request_ID
# request_id = get_next_sequence_value("request_id")
# print(f"Next Request_ID: {request_id}")