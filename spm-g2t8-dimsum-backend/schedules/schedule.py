from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
app.secret_key = os.getenv("SECRET_KEY")

# Helper functions for MongoDB access
def get_mongo_client():
    return MongoClient(os.getenv("DB_CON_STRING"))

def get_user_collection():
    client = get_mongo_client()
    user_db = client[os.getenv("DB_USERS")]
    return user_db[os.getenv("COLLECTION_USERS")]

def get_requests_collection():
    client = get_mongo_client()
    requests_db = client[os.getenv("DB_ARRANGEMENT")]
    return requests_db[os.getenv("COLLECTION_ARRANGEMENT")]

@app.route('/api/getSchedule', methods=['POST'])
def get_schedule():
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    data = request.json
    if not data or 'uid' not in data or 'date' not in data:
        return jsonify({"error": "Missing 'uid' or 'date' in request body"}), 404
    
    uid = data['uid']
    date_str = data['date']

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %B %Y")

    # Access collections through helper functions
    user_collection = get_user_collection()
    requests_collection = get_requests_collection()

    userData = user_collection.find_one({"Staff_ID": uid})
    if not userData:
        return jsonify({"error": "User not found"}), 404

    userDepartment = userData['Dept']
    userPosition = userData['Position']
    userRole = userData['Role']

    wfh = []
    wfh_ids = set()
    wfh_ids_am = set()
    wfh_ids_pm = set()
    inOffice = []

    if userRole == 2:
        teamMembers = list(user_collection.find({"Dept": userDepartment, "Position": userPosition})) if userDepartment not in ["Solutioning", "HR", "Engineering"] else list(user_collection.find({"Position": userPosition}))
        
        teamMembersDict = {member['Staff_ID']: member['Staff_FName'] + " " + member['Staff_LName'] for member in teamMembers}
        teamRequests = []
        
        for member in teamMembers:
            member_requests = list(requests_collection.find({"Staff_ID": member['Staff_ID'], "Apply_Date": date, "Status": {"$in": ["Pending", "Approved"]}}))
            teamRequests.extend(member_requests)

        for teamRequest in teamRequests:
            currMemberID = teamRequest['Staff_ID']
            currMemberName = teamMembersDict[currMemberID]
            wfh.append({"name": currMemberName, "id": currMemberID, "type": teamRequest['Duration'], "status": teamRequest['Status']})
            if teamRequest['Duration'] == "AM":
                wfh_ids_am.add(currMemberID)
            elif teamRequest['Duration'] == "PM":
                wfh_ids_pm.add(currMemberID)
            else:
                wfh_ids.add(currMemberID)

        for member in teamMembers:
            staff_id = member['Staff_ID']
            if staff_id not in wfh_ids and staff_id not in wfh_ids_am and staff_id not in wfh_ids_pm:
                inOffice.append({"name": teamMembersDict[staff_id], "type": "Full Day", "id": staff_id, "department": member['Dept']})
            elif staff_id in wfh_ids_am:
                inOffice.append({"name": teamMembersDict[staff_id], "type": "PM", "id": staff_id, "department": member['Dept']})
            elif staff_id in wfh_ids_pm:
                inOffice.append({"name": teamMembersDict[staff_id], "type": "AM", "id": staff_id, "department": member['Dept']})

        return jsonify({"wfh": wfh, "inOffice": inOffice}), 200
    elif userRole == 1:
        allMembers = list(user_collection.find({}))
        allMembersDict = {member['Staff_ID']: member['Staff_FName'] + " " + member['Staff_LName'] for member in allMembers}
        allMembersDeptDict = {member['Staff_ID']: member['Dept'] for member in allMembers}
        allRequests = list(requests_collection.find({"Apply_Date": date, "Status": {"$in": ["Pending", "Approved"]}}))
        
        for singleRequest in allRequests:
            currMemberID = singleRequest['Staff_ID']
            currMemberName = allMembersDict[currMemberID]
            wfh.append({"name": currMemberName, "id": currMemberID, "type": singleRequest['Duration'], "status": singleRequest['Status'], "department": allMembersDeptDict[currMemberID]})
            if singleRequest['Duration'] == "AM":
                wfh_ids_am.add(currMemberID)
            elif singleRequest['Duration'] == "PM":
                wfh_ids_pm.add(currMemberID)
            else:
                wfh_ids.add(currMemberID)

        for member in allMembers:
            staff_id = member['Staff_ID']
            if staff_id not in wfh_ids and staff_id not in wfh_ids_am and staff_id not in wfh_ids_pm:
                inOffice.append({"name": allMembersDict[staff_id], "type": "Full Day", "id": staff_id, "department": member['Dept']})
            elif staff_id in wfh_ids_am:
                inOffice.append({"name": allMembersDict[staff_id], "type": "PM", "id": staff_id, "department": member['Dept']})
            elif staff_id in wfh_ids_pm:
                inOffice.append({"name": allMembersDict[staff_id], "type": "AM", "id": staff_id, "department": member['Dept']})

        return jsonify({"wfh": wfh, "inOffice": inOffice}), 200
    elif userRole == 3:
        allMembers = [member for member in user_collection.find({"Dept": userDepartment}) if member['Position'] != 'Director']
        allMembersDict = {member['Staff_ID']: member['Staff_FName'] + " " + member['Staff_LName'] for member in allMembers}
        allRequests = list(requests_collection.find({"Apply_Date": date, "Status": {"$in": ["Pending", "Approved"]}, "Staff_ID": {"$in": [member['Staff_ID'] for member in allMembers]}}))

        for singleRequest in allRequests:
            currMemberID = singleRequest['Staff_ID']
            currMemberName = allMembersDict[currMemberID]
            wfh.append({"name": currMemberName, "id": currMemberID, "type": singleRequest['Duration'], "status": singleRequest['Status']})
            if singleRequest['Duration'] == "AM":
                wfh_ids_am.add(currMemberID)
            elif singleRequest['Duration'] == "PM":
                wfh_ids_pm.add(currMemberID)
            else:
                wfh_ids.add(currMemberID)

        for member in allMembers:
            staff_id = member['Staff_ID']
            if staff_id not in wfh_ids and staff_id not in wfh_ids_am and staff_id not in wfh_ids_pm:
                inOffice.append({"name": allMembersDict[staff_id], "type": "Full Day", "id": staff_id, "department": member['Dept']})
            elif staff_id in wfh_ids_am:
                inOffice.append({"name": allMembersDict[staff_id], "type": "PM", "id": staff_id, "department": member['Dept']})
            elif staff_id in wfh_ids_pm:
                inOffice.append({"name": allMembersDict[staff_id], "type": "AM", "id": staff_id, "department": member['Dept']})

        return jsonify({"wfh": wfh, "inOffice": inOffice}), 200

if __name__ == '__main__':
    app.run(debug=True)
