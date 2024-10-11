from flask import Flask, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
## Do pip install pymongo in your terminal
from pymongo import MongoClient


app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})


connection_string = "mongodb+srv://wxlum2022:PbQciwo6xIcw0eqt@assignment.9wecd.mongodb.net/"

app.secret_key = 'your_secret_key'

client = MongoClient(connection_string)
db = client['NewAssignment'] 
collection = db['NewAssignment']  


@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json  
    email = data['email']
    password = data['password']

    # Query the MongoDB collection to verify the email and Staff_ID (password)
    user = collection.find_one({"Email": email, "Staff_ID": int(password)})

    if user:
        staffName = user['Staff_FName'] + " " + user['Staff_LName']
        return jsonify({"status": "success", "message": f"Hello {user['Staff_FName']}!", 
                        "uid": user['Staff_ID'], "name": staffName, "role":user['Role']}), 200
    else:
        return jsonify({"status": "fail", "message": "Invalid email or password."}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5001)