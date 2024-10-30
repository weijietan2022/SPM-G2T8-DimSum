from flask import Flask, request, jsonify, flash, redirect, url_for,session
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app.secret_key = os.getenv("SECRET_KEY")

connection_string = os.getenv("DB_CON_STRING")
client = MongoClient(connection_string)
db = client[os.getenv("DB_USERS")]
collection = db[os.getenv("COLLECTION_USERS")]

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json  
    email = data['email']
    password = data['password']

    # Query the MongoDB collection to verify the email and Staff_ID (password)
    user = collection.find_one({"Email": email, "Staff_ID": int(password)})
    if user:
        session['ID'] = user['Staff_ID']
        session['Position'] = user['Position']
        session['Department'] = user['Dept']        
        staffName = user['Staff_FName'] + " " + user['Staff_LName']
        return jsonify({"status": "success", "message": f"Hello {user['Staff_FName']}!", 
                        "uid": user['Staff_ID'], "name": staffName, "role":user['Role'], "mid":user['Reporting_Manager'], "dept":user['Dept'], "position":user['Position']}), 200
    else:
        return jsonify({"status": "fail", "message": "Invalid email or password."}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5001)