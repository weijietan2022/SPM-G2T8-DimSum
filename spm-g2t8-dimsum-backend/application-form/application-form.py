from flask import Flask, jsonify, request, flash, send_file
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
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
collection = db_arrangement['Arrangement']  # Replace with your actual collection name

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

        results = list(collection.find(query))

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
            check_clash_query["$or"].append({"Duration": "Full Day"})
            check_clash_query["$or"].append({"Duration": "AM"})
            check_clash_query["$or"].append({"Duration": "PM"})
        elif duration == "AM":
            check_clash_query["$or"].append({"Duration": "AM"})
            check_clash_query["$or"].append({"Duration": "Full Day"})
        elif duration == "PM":
            check_clash_query["$or"].append({"Duration": "PM"})
            check_clash_query["$or"].append({"Duration": "Full Day"})

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
        

    # Get unique request_ID for this request
    request_id = get_next_sequence_value("request_id")

    for item in cart_items:
        date_obj = datetime.strptime(item['date'], '%Y-%m-%d')
        date = date_obj.strftime('%d %B %Y')
        duration = item['session']

        request_data = {
            "Request_ID": request_id,
            "Staff_ID": staff_ID,
            "Request_Date": datetime.now(),  # Proper datetime object
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

if __name__ == '__main__':
    app.run(debug=True, port=5002)
