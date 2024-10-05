from pymongo import MongoClient
from datetime import datetime

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific database
db = client['Arrangement']

# Define schema validation rules for "Arrangement" collection
validation_rules = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["Request_ID", "Staff_ID","Request_Date", "Apply_Date", "Duration", "Manager_ID", "Status"],
        "properties": {
            "Request_ID": {
                "bsonType": "int",
                "description": "Request_ID must be an integer and is auto-incremeneted."
            },
            "Staff_ID": {
                "bsonType": "int",
                "description": "Staff_ID must be an integer and is required."
            },
            "Request_Date": {
                "bsonType": "date",
                "description": "Request_Date must be a date and is required."
            },
            "Apply_Date": {
                "bsonType": "string",
                "description": "Apply_Date must be a string and is required."
            },
            "Duration": {
                "bsonType": "string",
                "enum": ["AM", "PM", "Full Day"],
                "description": "Duration must be either 'AM', 'PM', or 'Full Day' and is required."
            },
            "Manager_ID": {
                "bsonType": "int",
                "description": "Manager_ID must be an integer and is required."
            },
            "Status": {
                "bsonType": "string",
                "maxLength": 20,
                "description": "Status must be a string with a max length of 20 characters and is required."
            },
        }
    }
}

# Create the "APPLY REQUEST" collection with schema validation
db.create_collection("Arrangement", validator=validation_rules)

# Create a composite key index (Request_ID and Apply_Date should be unique together)
db['Arrangement'].create_index(
    [("Request_ID", 1), ("Apply_Date", 1)], 
    unique=True
)

print("Arrangement collection created with schema validation and composite key index.")

# # Insert a sample document into the collection using datetime objects
# apply_request_data = {
#     "Request_ID": 1,
#     "Staff_ID": 1001,
#     "Request_Date": datetime.now(),  # Proper datetime object
#     "Apply_Date": datetime(2024, 10, 1),
#     "Duration": "AM",
#     "Manager_ID": 5001,
#     "Status": "Pending",
# }

# # Insert into the collection
# try:
#     db['Arrangement'].insert_one(apply_request_data)
#     print("Sample document inserted.")
# except Exception as e:
#     print(f"Insert error: {e}")