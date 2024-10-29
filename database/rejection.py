from pymongo import MongoClient
from datetime import datetime

connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

db = client['Rejection']

validation_rules = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["Request_ID", "Staff_ID","Request_Date", "Apply_Date", "Duration", "Manager_ID", "Reason", "Reject_Date_Time"],
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
            "Reject_Date_Time": {
                "bsonType": "date",
                "description": "Reject_Date_Time must be a date and is required."
            }
        }
    }
}

db.create_collection("Rejection", validator=validation_rules)

db['Rejection'].create_index(
    [("Request_ID", 1), ("Apply_Date", 1)], 
    unique=True
)

print("Rejection collection created with schema validation and composite key index.")