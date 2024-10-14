from flask import Flask, jsonify, request, redirect, url_for, flash, render_template, session
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
# from database.counter import get_next_sequence_value
import gridfs
import json


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.secret_key = 'your_secret_key'

# MongoDB connection
connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)
db_arrangement = client['NewArrangement'] 

# Define your collection
collection = db_arrangement['Arrangement']  # Replace with your actual collection name


def serialize_data(data):
    """ Convert MongoDB BSON types to JSON serializable types. """
    if isinstance(data, ObjectId):
        return str(data)  # Convert ObjectId to string
    if isinstance(data, datetime):
        return data.isoformat()  # Convert datetime to ISO format string
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    return data

@app.route('/api/view-request', methods=['GET'])
def getRequest():
    # Hardcoded values for now (simulating session data)
    id = 151408
    Position = 'Director'
    Dept = 'Engineering'
    
    # Fetch the requests based on position
    requests = ViewRequest(id, Position, Dept)

    # Serialize the requests and return them as a JSON response
    return jsonify([serialize_data(req) for req in requests])

def ViewRequest(id, Position, Dept):
    if Position == 'MD':
        # Query MongoDB for pending requests
        requests = collection.find({"Status": "Pending"})
    elif Position == 'Director':
        deptStaff = list(collection.find({"Department": Dept}, {"Staff_ID": 1}))
        Dept_ids = [staff["Staff_ID"] for staff in deptStaff]
        requests = collection.find({
            "Staff_ID": {"$in": Dept_ids}, 
            "Status": "Pending"
        })
    elif "Manager" in Position:
        direct_reports = list(collection.find({"Manager_ID": id, "Department": Dept}, {"Staff_ID": 1}))
        ids = [report["Staff_ID"] for report in direct_reports]
        requests = collection.find({
            "Staff_ID": {"$in": ids}, 
            "Department": Dept, 
            "Status": "Pending"
        })

    # Return the MongoDB cursor as a list for easy iteration
    return list(requests)

@app.route('/api/requests', methods=['GET'])
def get_requests():
    # Retrieve the status filter from query parameters if provided
    status = request.args.get('status', None)
    
    # Build query depending on whether status filter is provided
    query = {}
    if status:
        query['Status'] = status
    
    # Fetch data from MongoDB
    results = list(collection.find(query))
    
    # Convert results to JSON-serializable format
    serialized_results = [serialize_data(result) for result in results]
    
    return jsonify(serialized_results)

if __name__ == '__main__':
    app.run(debug=True, port=5008)

