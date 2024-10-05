from pymongo import MongoClient
from datetime import datetime

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific database
db = client['Rejected']

# Define schema validation rules for "Rejected" collection
validation_rules = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["Request_ID", "Staff_ID","Request_Date", "Apply_Date", "Duration", "Manager_ID", "Reason"],
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
            "Reason": {
                "bsonType": "string",
                "maxLength": 255,
                "description": "Status must be a string with a max length of 255 characters and is required."
            },
        }
    }
}

# Create the "Rejected" collection with schema validation
db.create_collection("Rejected", validator=validation_rules)

# Create a composite key index (Request_ID and Apply_Date should be unique together)
db['Rejected'].create_index(
    [("Request_ID", 1), ("Apply_Date", 1)], 
    unique=True
)

print("Rejected collection created with schema validation and composite key index.")