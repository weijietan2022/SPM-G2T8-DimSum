from flask import Flask, jsonify, request, redirect, url_for, flash, render_template, session
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta

import gridfs
import json


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.secret_key = 'your_secret_key'

# MongoDB connection
connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)
db_arrangement = client['Arrangement'] 

# Define your collection
collection = db_arrangement['Arrangement']  

db_new_assignment = client['NewAssignment']
collection_new_assignment = db_new_assignment['NewAssignment']


def serialize_data(data):
    """ Convert MongoDB BSON types to JSON serializable types. """
    if isinstance(data, ObjectId):
        return str(data)  
    if isinstance(data, datetime):
        return data.isoformat()  
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    return data

@app.route('/api/view-request', methods=['GET'])
def getRequest():


    Dept = request.args.get('dept')
    id = request.args.get('staffId')
    id = int(id)
    Position = request.args.get('position')
    
  
    
    stat = request.args.get('status', 'Pending')

    requests = ViewRequest(id, Position, Dept,stat)
    print(f"Returning requests for status {stat}: {requests}")

    enriched_requests = []
    for req in requests:
        staff_id = req.get("Staff_ID")
        staff_data = collection_new_assignment.find_one({"Staff_ID": staff_id})
        if staff_data and "Dept" in staff_data:
            req["Department"] = staff_data["Dept"]
        
        enriched_requests.append(req)

    return jsonify([serialize_data(req) for req in enriched_requests])


    # Serialize the requests and return them as a JSON response
    return jsonify([serialize_data(req) for req in requests])
def ViewRequest(id, Position, Dept, status):
    query = {}

    if status != 'All':
        query["Status"] = status

    if Position == 'MD':
        requests = collection.find(query)

    # elif Position == 'Director':
    #     # Director sees all requests in their department filtered by status
    #     deptStaff = list(collection.find({"Department": Dept}, {"Staff_ID": 1}))
    #     Dept_ids = [staff["Staff_ID"] for staff in deptStaff]
    #     query["Staff_ID"] = {"$in": Dept_ids}
    #     requests = collection.find(query)

    elif "Manager" in Position or Position == "Director":
        listofids = list(collection.find({"Manager_ID": id}, {"Staff_ID": 1, "_id": 0}))
        if listofids:
            ids = [report["Staff_ID"] for report in listofids]
            query["Staff_ID"] = {"$in": ids}

            requests = collection.find(query)
        else:
            print("No report found")
            requests = []

    return list(requests)


@app.route('/api/requests', methods=['GET'])
def get_requests():
    status = request.args.get('status', None)
    
    query = {}
    if status:
        query['Status'] = status
    
    results = list(collection.find(query))
    
    serialized_results = [serialize_data(result) for result in results]
    
    return jsonify(serialized_results)

@app.route('/api/update-request', methods=['POST'])
def update_request_status():
    data = request.json
    request_id = data.get('requestId')
    new_status = data.get('status')

    if not request_id or new_status not in ['Approved', 'Rejected']:
        return jsonify({"error": "Invalid request data"}), 400

    # Update the status in the database
    result = collection.update_one(
        {"Request_ID": request_id},
        {"$set": {"Status": new_status}}
    )

    if result.modified_count == 1:
        return jsonify({"message": f"Request {new_status} successfully."}), 200
    else:
        return jsonify({"error": "Failed to update request status"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5008)

