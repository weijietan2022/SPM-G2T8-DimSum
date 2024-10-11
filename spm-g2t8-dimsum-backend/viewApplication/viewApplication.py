from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# MongoDB connection
connection_string = "mongodb+srv://wxlum2022:PbQciwo6xIcw0eqt@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)
db_arrangement = client['Arrangement'] 

# Define your collection
collection = db_arrangement['Arrangement']  # Replace with your actual collection name

def serialize_data(data):
    """ Convert MongoDB BSON types to JSON serializable types. """
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, datetime):
        return data.isoformat()  # Convert datetime to ISO format string
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    return data

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
    app.run(debug=True, port=5002)
