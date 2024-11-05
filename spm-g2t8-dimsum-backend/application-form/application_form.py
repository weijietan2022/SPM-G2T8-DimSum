from flask import Flask, jsonify, request, flash, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import gridfs
import json
from dotenv import load_dotenv
from pathlib import Path
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
app.secret_key = os.getenv("SECRET_KEY")

# MongoDB initialization helpers
def init_mongo_client():
    """Initialize MongoDB client using connection string from environment variables."""
    connection_string = os.getenv("DB_CON_STRING")
    return MongoClient(connection_string)

def get_db(client, db_name_env_var):
    """Get a database instance based on environment variable name."""
    return client[os.getenv(db_name_env_var)]

def get_collection(db, collection_name_env_var):
    """Get a collection from a specified database based on environment variable name."""
    return db[os.getenv(collection_name_env_var)]

def get_fs(client):
    """Get a GridFS instance based on environment variable name."""
    return gridfs.GridFS(client['file_storage'])

def get_counters_collection(db):
    """Get the 'counters' collection from a specified database."""
    return db['counters']


# Initialize MongoDB client and collections
client = init_mongo_client()

db_new_assignment = get_db(client, "DB_USERS")
collection_new_assignment = get_collection(db_new_assignment, "COLLECTION_USERS")

db_arrangement = get_db(client, "DB_ARRANGEMENT")
collection = get_collection(db_arrangement, "COLLECTION_ARRANGEMENT")

db_rejection = get_db(client, "DB_REJECTION")
collection_rejection = get_collection(db_rejection, "COLLECTION_REJECTION")


# file_storage = client['file_storage']
# fs = gridfs.GridFS(file_storage)
fs = get_fs(client)


def get_next_sequence_value(sequence_name):
    """Get the next value of a sequence from the 'counters' collection."""
    counters_collection = get_counters_collection(db_arrangement)
    sequence_document = counters_collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        return_document=True
    )
    return sequence_document["sequence_value"]


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


@app.route('/api/requests', methods=['GET'])
def get_requests():
    try:
        status = request.args.get('status', None)
        staff_id = request.args.get('staff_id', None)

        query = {}
        if status:
            query['Status'] = status
        if staff_id:
            query['Staff_ID'] = int(staff_id)

        results = list(collection.find(query).sort("Request_Date", -1))

        serialized_results = []

        for result in results:
            serialized_result = serialize_data(result)
            
            if result['File'] != None:
                serialized_result['File'] = str(result['File'])
            
            serialized_results.append(serialized_result)

        return jsonify(serialized_results), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch requests", "details": str(e)}), 500


##################################################################################
##################################################################################


@app.route('/api/files/<file_id>', methods=['GET'])
def download_file(file_id):
    try:        
        if not ObjectId.is_valid(file_id):
            return jsonify({"error": "Invalid file ID"}), 400
        
        print(file_id)
        file = fs.get(ObjectId(file_id))
        
        return send_file(file, download_name=file.filename, as_attachment=True)
    
    except gridfs.errors.NoFile:
        return jsonify({"error": "File not found"}), 404
    
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


##################################################################################
##################################################################################


# processing WFH request form
@app.route('/api/process_request', methods=['POST'])
def process():
    cart = request.form.get('date')
    reason = request.form.get('reason')
    file = request.files.get('attachment')
    staff_ID = int(request.form.get('staffId'))
    manager_ID = int(request.form.get('managerId'))

    if not cart or not reason or not staff_ID or not manager_ID:
        return jsonify({"status": "fail", "message": "Missing required fields."}), 400
    
    try:
        cart_items = json.loads(cart)
        if not cart_items:
            return jsonify({"status": "fail", "message": "No dates provided in the cart."}), 400
    except json.JSONDecodeError:
        return jsonify({"status": "fail", "message": "Invalid cart format."}), 400

    # Process the uploaded file if it exists
    file_id = None
    if file:
        file_id = fs.put(file, filename=file.filename)

    clashing_records = []

    # Check database for duplicates
    cart_items = json.loads(cart)

    for item in cart_items:
        date_obj = datetime.strptime(item['date'], '%Y-%m-%d')
        date = date_obj.strftime('%d %B %Y')
        duration = item['session']

        ## Check if date is on the immediate next working day
        if date == get_next_working_day():
            return jsonify({"success": False, "message": "Cannot apply for WFH on the next working day."}), 400
        
        ## If date is today, cannot applt
        if date == datetime.now().strftime('%d %B %Y'):
            return jsonify({"success": False, "message": "Cannot apply for WFH on the same day."}), 400

        check_clash_query = {
            "Staff_ID": staff_ID,
            "Apply_Date": date,
            "$or": []
        }

        # clashing conditions based on duration
        if duration == "Full Day":
            check_clash_query["$or"].append({"Duration": "Full Day", "Status": {"$in": ["Approved", "Pending"]}})
            check_clash_query["$or"].append({"Duration": "AM", "Status": {"$in": ["Approved", "Pending"]}})
            check_clash_query["$or"].append({"Duration": "PM", "Status": {"$in": ["Approved", "Pending"]}})
        elif duration == "AM":
            check_clash_query["$or"].append({"Duration": "AM", "Status": {"$in": ["Approved", "Pending"]}})
            check_clash_query["$or"].append({"Duration": "Full Day", "Status": {"$in": ["Approved", "Pending"]}})
        elif duration == "PM":
            check_clash_query["$or"].append({"Duration": "PM", "Status": {"$in": ["Approved", "Pending"]}})
            check_clash_query["$or"].append({"Duration": "Full Day", "Status": {"$in": ["Approved", "Pending"]}})

        existing_record = collection.find_one(check_clash_query)

        if existing_record:    
            clashing_records.append(existing_record)

    # If any clash records exist, prepare a message
    if clashing_records:
        clash_messages = []
        for record in clashing_records:
            clash_date = record["Apply_Date"]
            clash_duration = record["Duration"]
            clash_string = f"Clash found for {clash_date} with duration {clash_duration}."
            if clash_string not in clash_messages:
                clash_messages.append(clash_string)

        return jsonify({"success": False, "message": clash_messages}), 400
        

    request_id = get_next_sequence_value("request_id")
    dates = []
    types = []
    for item in cart_items:
        date_obj = datetime.strptime(item['date'], '%Y-%m-%d')
        date = date_obj.strftime('%d %B %Y')
        dates.append(date)
        duration = item['session']
        types.append(duration)

        request_data = {
            "Request_ID": request_id,
            "Staff_ID": staff_ID,
            "Request_Date": datetime.now(),
            "Apply_Date": date,
            "Duration": duration,
            "Reason": reason,
            "Manager_ID": manager_ID,
            "Status": "Pending",
            "File": file_id
        }

        try:
            collection.insert_one(request_data)
            
        except Exception as e:
            flash(f"Error in putting in DB")
            return jsonify({"status": "fail", "message": "Error inserting request into database."}), 401
        
    # Send notification to manager
    try:
        manager_details = collection_new_assignment.find_one({"Staff_ID": manager_ID})
        manager_email = manager_details.get("Email")
        manager_name = manager_details.get("Staff_FName") + " " + manager_details.get("Staff_LName")
        employee_details = collection_new_assignment.find_one({"Staff_ID": staff_ID})
        employee_name = employee_details.get("Staff_FName") + " " + employee_details.get("Staff_LName")
    except Exception as e:
        return jsonify({"status": "success", "message": "request inserted without notification"}), 200

    if not send_notification(employee_name, manager_email, manager_name, request_id, dates, types):
        return jsonify({"status": "success", "message": "request inserted but manager notification failed"}), 200

    return jsonify({"status": "success", "message": "request inserted and manager notified"}), 200

def send_notification(employee_name, manager_email, manager_name, request_id, dates, types):
    """Helper function to send notification to the manager."""
    notification_URL = "http://127.0.0.1:5003/api/sendRequestNotification"
    notification_data = {
        "name": employee_name,
        "managerEmail": manager_email,
        "managerName": manager_name,
        "requestId": request_id,
        "dates": dates,
        "type": types
    }

    response = requests.post(notification_URL, json=notification_data)
    if response.status_code != 200:
        return False
    return True


## Helper function
def get_next_working_day():
    today = datetime.now().date()
    next_day = today + timedelta(days=1)
    
    # Skip weekends
    if next_day.weekday() == 5:  # Saturday
        next_day += timedelta(days=2)
    elif next_day.weekday() == 6:  # Sunday
        next_day += timedelta(days=1)
    
    return next_day.strftime('%d %B %Y')

@app.route('/api/withdraw', methods=['POST'])
def withdraw_request():
    data = request.json
    request_id = data.get('requestId')
    apply_date = data.get('applyDate')
    managerId = data.get('managerId')
    duration = data.get('duration')
    staffId = data.get('staffId')
    status = data.get('status')

    if (status == "Approved"):
        try:
            ManagerDetails = collection_new_assignment.find_one({"Staff_ID":managerId})
            manager_email = ManagerDetails.get("Email")
            manager_fname = ManagerDetails.get("Staff_FName")
            manager_lname = ManagerDetails.get("Staff_LName")
            manager_name = manager_fname + " " + manager_lname
        except Exception as e:
                return jsonify({"error": "An error occurred", "details": str(e)}), 500  

        try:
            EmployeeDetails = collection_new_assignment.find_one({"Staff_ID":staffId})
            emp_fname = EmployeeDetails.get("Staff_FName")
            emp_lname = EmployeeDetails.get("Staff_LName")
            emp_name = emp_fname + " " + emp_lname
        except Exception as e:
                return jsonify({"error": "An error occurred", "details": str(e)}), 500
    
        notification_details = {
            "name": emp_name,
            "managerEmail": manager_email,
            "managerName": manager_name,
            "requestId": request_id,
            "date": apply_date,
            "type": duration
        } 

        try:
            result = collection.update_one(
                {
                    "Request_ID": int(request_id),
                    "Apply_Date": apply_date
                },
                {
                    "$set": {
                        "Status": "Withdrawn"
                    }
                }
            )
            
            if result.modified_count > 0:
                Notifresponse = send_cancel_notification(notification_details)
                if Notifresponse:
                    print("Withdrawal Notification sent successfully.")
                else:
                    print(f"Failed to send notification: {Notifresponse.json()}")
                return jsonify({"message": "Request successfully withdrawn"}), 200
            else:
                return jsonify({"message": "Failed to update database"}), 404
        except Exception as e:
            return jsonify({"error": "No such document in the database"}), 404
        
    else:
        try:
            result = collection.update_one(
                {
                    "Request_ID": int(request_id),
                    "Apply_Date": apply_date
                },
                {
                    "$set": {
                        "Status": "Withdrawn"
                    }
                }
            )

            if result.modified_count > 0:
                return jsonify({"message": "Request successfully withdrawn"}), 200
            else:
                return jsonify({"message": "Request not found or already withdrawn"}), 404
        except Exception as e:
            return jsonify({"error": "No such document in the database"}), 404
        
def send_cancel_notification(notification_data):
    """Helper function to send notification to the manager."""
    notification_URL = "http://127.0.0.1:5003/api/sendCancellationNotification"

    employee_name = notification_data.get("name")   
    manager_email = notification_data.get("managerEmail")
    manager_name = notification_data.get("managerName")
    request_id = notification_data.get("requestId")
    date = notification_data.get("date")
    type = notification_data.get("type")

    notification_data = {
        "name": employee_name,
        "managerEmail": manager_email,
        "managerName": manager_name,
        "requestId": request_id,
        "date": date,
        "type": type
    }  

    response = requests.post(notification_URL, json=notification_data)
    if response.status_code != 200:
        return False
    return True
        
@app.route('/api/getRejectionReason', methods=['POST'])
def get_rejection_reason():

    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400

    data = request.json

    # Check if the request_id and apply_date are provided
    if 'request_id' not in data or 'apply_date' not in data:
        return jsonify({"error": "Missing 'request_id' or 'apply_date' in request body"}), 400

    request_id = data.get('request_id')
    apply_date = data.get('apply_date')
    try:
        rejection_record = collection_rejection.find_one({"Request_ID": int(request_id), "Apply_Date": apply_date})
        if rejection_record:
            return jsonify({"reason": rejection_record.get("Reason")}), 200
        else:
            return jsonify({"error": "Request not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=5002)
