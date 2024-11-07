from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import gridfs

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific database
db_arrangement = client['Arrangement']

# Delete all existing documents in the collection
db_arrangement['Arrangement'].delete_many({})

# Delete all from Rejection collection
db_rejection = client['Rejection']
db_rejection['Rejection'].delete_many({})

# Delete all from the approval collection
db_approval = client['Approval']
db_approval['Approval'].delete_many({})
