from pymongo import MongoClient

connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

db = client['Approval']

validation_rules = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["Request_ID", "Apply_Date", "Manager_ID", "Approve_Date_Time"],
        "properties": {
            "Request_ID": {
                "bsonType": "int",
                "description": "Request_ID must be an integer and is auto-incremeneted."
            },
            "Apply_Date": {
                "bsonType": "string",
                "description": "Apply_Date must be a string and is required."
            },
            "Manager_ID": {
                "bsonType": "int",
                "description": "Manager_ID must be an integer and is required."
            },
            "Approve_Date_Time": {
                "bsonType": "date",
                "description": "Approve_Date_Time must be a date and is required."
            }
        }
    }
}

db.create_collection("Approval", validator=validation_rules)

db['Approval'].create_index(
    [("Request_ID", 1), ("Apply_Date", 1)], 
    unique=True
)

print("Approval collection created with schema validation and composite key index.")