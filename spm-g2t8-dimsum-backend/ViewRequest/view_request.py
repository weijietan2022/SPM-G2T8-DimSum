from flask import Flask, jsonify, request, redirect, url_for, flash, render_template, session, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os
import gridfs
import json


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
app.secret_key = os.getenv("SECRET_KEY")

# MongoDB connection
connection_string = os.getenv("DB_CON_STRING")
client = MongoClient(connection_string)
db_arrangement = client[os.getenv("DB_ARRANGEMENT")]
collection = db_arrangement[os.getenv("COLLECTION_ARRANGEMENT")]

db_new_assignment = client[os.getenv("DB_USERS")]
collection_new_assignment = db_new_assignment[os.getenv("COLLECTION_USERS")]

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
    # print(f"Returning requests for status {stat}: {requests}")

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
    print(new_status)

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
    
@app.route('/api/files/<file_id>', methods=['GET'])
def download_file(file_id):
    try:
        print(f"Received file ID: {file_id}")
        
        if not ObjectId.is_valid(file_id):
            return jsonify({"error": "Invalid file ID"}), 400
        
        file = fs.get(ObjectId(file_id))
        
        return send_file(file, download_name=file.filename, as_attachment=True)
    
    except gridfs.errors.NoFile:
        print(f"No file found with ID: {file_id}")
        return jsonify({"error": "File not found"}), 404
    
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500
    

@app.route('/api/reject-request', methods=['POST'])
def reject_request():
    data = request.json
    request_id = data.get('Request_ID')
    staff_id = data.get('Staff_ID')
    request_date = data.get('Request_Date')
    apply_date = data.get('Apply_Date')
    duration = data.get('Duration')
    manager_id = data.get('Manager_ID')
    reason = data.get('Reason')
    status = 'Rejected'

    rejected = {
        "Request_ID": request_id,
        "Staff_ID": staff_id,
        "Request_Date": request_date,
        "Apply_Date": apply_date,
        "Duration": duration,
        "Reason": reason,
        "Manager_ID": manager_id,
        "Status": status,
        "File": "Null"
    }
    
    try:
        Reject_Collection.insert_one(rejected)
        return jsonify({"message": "Rejection submitted successfully"}), 200
    except Exception as e:
        print("Error", e)
        return jsonify({"error": "Failed to submit into rejected database"}), 500




if __name__ == '__main__':
    app.run(debug=True, port=5008)

