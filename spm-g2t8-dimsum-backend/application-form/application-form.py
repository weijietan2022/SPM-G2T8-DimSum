from flask import Flask, jsonify, request, flash, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import gridfs
import json
from dotenv import load_dotenv
from pathlib import Path
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app.secret_key = os.getenv("SECRET_KEY")

# MongoDB connection
connection_string = os.getenv("DB_CON_STRING")
client = MongoClient(connection_string)
db_arrangement = client[os.getenv("DB_ARRANGEMENT")]
collection = db_arrangement[os.getenv("COLLECTION_ARRANGEMENT")]

file_storage = client['file_storage']
fs = gridfs.GridFS(file_storage)

def get_next_sequence_value(sequence_name):
    result = db_arrangement['counters'].find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        return_document=True
    )
    return result['sequence_value']


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

        print(f"Query: {query}")

        results = list(collection.find(query).sort("Request_Date", -1))

        serialized_results = []
        for result in results:
            serialized_result = serialize_data(result)
            
            if result['File'] != None:
                serialized_result['File'] = str(result['File'])
            
            serialized_results.append(serialized_result)
        print(serialized_results)

        return jsonify(serialized_results), 200
    except Exception as e:
        print(f"Error fetching requests: {str(e)}")
        return jsonify({"error": "Failed to fetch requests", "details": str(e)}), 500


##################################################################################
##################################################################################


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

    print("This is the file")
    print(file)

    if not cart or not reason:
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
        print(date_obj)
        date = date_obj.strftime('%d %B %Y')
        duration = item['session']

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

        existing_record = db_arrangement["Arrangement"].find_one(check_clash_query)

        if existing_record:    
            clashing_records.append(existing_record)
            print(existing_record)

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

    for item in cart_items:
        date_obj = datetime.strptime(item['date'], '%Y-%m-%d')
        date = date_obj.strftime('%d %B %Y')
        duration = item['session']

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
            db_arrangement['Arrangement'].insert_one(request_data)
            print("request inserted.")
            
        except Exception as e:
            print(f"Insert error: {e}")
            flash(f"Error in putting in DB")
            return jsonify({"status": "fail", "message": "Error inserting request into database."}), 401

    return jsonify({"status": "success", "message": "request inserted"}), 200


@app.route('/api/withdraw/<request_id>/<apply_date>', methods=['PUT'])
def withdraw_request(request_id, apply_date):
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
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=5002)
