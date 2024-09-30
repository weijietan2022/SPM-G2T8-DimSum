import pymongo
from pymongo import MongoClient

connection_string = "mongodb+srv://wxlum2022:PbQciwo6xIcw0eqt@assignment.9wecd.mongodb.net/"

client = MongoClient(connection_string)

db=client['NewAssignment']

collection=db['NewAssignment']

query = {"Staff_ID":140881}

document=collection.find_one(query)

if document:
    print(document)
else:
    print("No document found")