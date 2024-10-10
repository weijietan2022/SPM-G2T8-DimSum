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
        "required": ["Request_ID", "Staff_ID","Request_Date", "Apply_Date", "Duration", "Reason", "Manager_ID", "Status", "File"],
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
            "Reason": {
                "bsonType": "string",
                "maxLength": 255,
                "description": "Status must be a string with a max length of 255 character and is required."
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
            "File": {
                "bsonType": ["objectId", "null"],
                "description": "File must be an ObjectId if a file is uploaded and is optional"
            }
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