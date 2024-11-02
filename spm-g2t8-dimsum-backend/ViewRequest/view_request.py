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
import requests


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


db_approval = client[os.getenv("DB_APPROVAL")]
collection_approval = db_approval[os.getenv("COLLECTION_APPROVAL")]


db_rejection = client[os.getenv("DB_REJECTION")]
Reject_Collection = db_rejection[os.getenv("COLLECTION_REJECTION")]


file_storage = client['file_storage']
fs = gridfs.GridFS(file_storage)

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

    print("Received request with parameters:")
    print(Dept, id, Position, stat)

    requests = ViewRequest(id, Position, Dept,stat)

    enriched_requests = []
    for req in requests:
        staff_id = req.get("Staff_ID")
        staff_data = collection_new_assignment.find_one({"Staff_ID": staff_id})
        if staff_data and "Dept" in staff_data:
            req["Department"] = staff_data["Dept"]
            F_Name = staff_data.get('Staff_FName', "")
            L_Name = staff_data.get('Staff_LName', "")
            name = f"{F_Name} {L_Name}".strip()
            req["name"] = name
        
        enriched_requests.append(req)

    return jsonify([serialize_data(req) for req in enriched_requests])


    
    return jsonify([serialize_data(req) for req in requests])
def ViewRequest(id, Position, Dept, status):
    query = {}

    if status != 'All':
        query["Status"] = status

    if "Manager" in Position or Position == "Director" or Position =='MD':
        listofids = list(collection.find({"Manager_ID": id}, {"Staff_ID": 1, "_id": 0}))
        print(listofids)
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
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    ## Check if the request body contains the required fields
    if 'requestId' not in request.json or 'status' not in request.json or 'date' not in request.json or 'duration' not in request.json:
        return jsonify({"error": "Missing information in request body"}), 400

    data = request.json
    request_id = data.get('requestId')
    new_status = data.get('status')
    date = data.get('date')
    duration = data.get('duration')
    print(new_status)

    if not request_id or new_status not in ['Approved', 'Rejected']:
        return jsonify({"error": "Invalid request data"}), 400

    # Check if the request exists in the database
    requestToUpdate = collection.find_one({"Request_ID": request_id, "Apply_Date": date, "Duration": duration})
    if not requestToUpdate:
        return jsonify({"error": "Request not found."}), 404

    # Update the status in the database
    try:
        collection.update_one({"Request_ID": request_id, "Apply_Date": date, "Duration": duration}, {"$set": {"Status": new_status}})
    except Exception as e:
        print(f"Error updating request status: {str(e)}")
        return jsonify({"error": "Failed to update request status"}), 500
    
    return jsonify({"message": f"Request {new_status} successfully."}), 200

    # if result.modified_count == 1:
    #     return jsonify({"message": f"Request {new_status} successfully."}), 200
    # else:
    #     return jsonify({"error": "Failed to update request status"}), 500
    
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
    print(request.json)
    data = request.json
    request_id = data.get('Request_ID')
    staff_id = data.get('Staff_ID')
    request_date = data.get('Request_Date')
    # request_date = datetime.fromisoformat(request_date) if isinstance(request_date, str) else request_date
    request_date = datetime.strptime(request_date, '%a, %d %b %Y %H:%M:%S %Z')
    apply_date = data.get('Apply_Date')
    duration = data.get('Duration')
    manager_id = data.get('Manager_ID')
    rejectionReason = data.get('rejectionReason')
    status = 'Rejected'
    print(rejectionReason)
    try:
             EmployeeDetails = collection_new_assignment.find_one({"Staff_ID":staff_id})
             email = EmployeeDetails.get("Email")
             print(email)
             fname = EmployeeDetails.get("Staff_FName")
             lname = EmployeeDetails.get("Staff_LName")
             name = fname + " " + lname  
    except Exception as e:
            print(f"There is an error: {str(e)}")
            return jsonify({"error": "An error occurred", "details": str(e)}), 500

    rejected = {
        "Request_ID": request_id,
        "Staff_ID": staff_id,
        "Request_Date": request_date,
        "Apply_Date": apply_date,
        "Duration": duration,
        "Manager_ID": manager_id,
        "Reason": rejectionReason,
        "Reject_Date_Time": datetime.now()
    }

    ## Get manager email
    managerObject = collection_new_assignment.find_one({"Staff_ID": manager_id})
    managerEmail = managerObject.get("Email")

    Notification = {
            "requestId": request_id,
            "date": apply_date,
            "email": managerEmail,
            "name": name, 
            "type": duration
        }
    
    notification_URL = "http://127.0.0.1:5003/api/sendRejectionNotification"
    Notifresponse = requests.post(notification_URL, json=Notification)
    if Notifresponse.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification: {Notifresponse.json()}")
    
    try:
        Reject_Collection.insert_one(rejected)
        return jsonify({"message": "Rejection submitted successfully"}), 200
    except Exception as e:
        print("Error", e)
        return jsonify({"error": "Failed to submit into rejected database"}), 500
    

@app.route('/api/approve-request', methods=['POST'])
def approve_request():
    data = request.json
    request_ID = data.get('requestId')
    date = data.get('date')
    duration = data.get('duration')
    if not request_ID:
        return jsonify({"Error":"No request_ID"})
    try:
        requestDetails = collection.find_one({"Request_ID":request_ID, "Apply_Date": date, "Duration": duration})
        if not requestDetails:
            return jsonify({"Error": "Request is not found"})
        Apply_Date = requestDetails.get("Apply_Date")
        ManagerID = requestDetails.get("Manager_ID")
        StaffID = requestDetails.get("Staff_ID")
        typeofreq = requestDetails.get("Duration")
        try:
             EmployeeDetails = collection_new_assignment.find_one({"Staff_ID":StaffID})
             email = EmployeeDetails.get("Email")
             print(email)
             fname = EmployeeDetails.get("Staff_FName")
             lname = EmployeeDetails.get("Staff_LName")
             name = fname + " " + lname  
        except Exception as e:
            print(f"There is an error: {str(e)}")
            return jsonify({"error": "An error occurred", "details": str(e)}), 500
        
        # change to your own email to test
        Notification = {
            "requestId": request_ID,
            "date": Apply_Date,
            "email": "weenxiaang@gmail.com",
            "name": name, 
            "type": typeofreq
        }

        notification_URL = "http://127.0.0.1:5003/api/sendApprovalNotification"
        Notifresponse = requests.post(notification_URL, json=Notification)
        if Notifresponse.status_code == 200:
            print("Notification sent successfully.")
        else:
            print(f"Failed to send notification: {Notifresponse.json()}")

        Approved = {    
            "Request_ID": request_ID,
            "Apply_Date": Apply_Date,
            "Manager_ID": ManagerID,
            "Approve_Date_Time": datetime.now()
        }
        collection_approval.insert_one(Approved)

        return jsonify({"message": "Request Approved successfully."}), 200
    
    except Exception as e:
                print(f"There is an error: {str(e)}")
                return jsonify({"error": "An error occurred", "details": str(e)}), 500





if __name__ == '__main__':
    app.run(debug=True, port=5008)

