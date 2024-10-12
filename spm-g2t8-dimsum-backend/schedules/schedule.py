from flask import Flask, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime


app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

connection_string = "mongodb+srv://wxlum2022:PbQciwo6xIcw0eqt@assignment.9wecd.mongodb.net/"

app.secret_key = 'your_secret_key'

client = MongoClient(connection_string)
userDb = client['NewAssignment'] 
userCollection = userDb['NewAssignment']  

requestsDb = client['Arrangement']
requestsCollection = requestsDb['Arrangement']


@app.route('/api/getSchedule', methods=['POST'])
def get_schedule():
    if not request.is_json:
        print("Request must be in JSON format")
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    data = request.json
    if not data or 'uid' not in data or 'date' not in data:
        print("Missing 'uid' or 'date' in request body")
        return jsonify({"error": "Missing 'uid' or 'date' in request body"}), 400
    
    uid = data['uid']
    date_str = data['date']

    date = datetime.strptime(date_str, "%Y-%m-%d")
    date = date.strftime("%d %B %Y")

    print(date)
    
    userData = userCollection.find_one({"Staff_ID": uid})
    if not userData:
        return jsonify({"error": "User not found"}), 404
    
    userDepartment = userData['Dept']
    userPosition = userData['Position']
    userRole = userData['Role']

    wfh = []
    wfh_ids = set()
    inOffice = []

    if userRole == 2:
        teamMembers = []
    
        if userDepartment in ["Solutioning", "HR", "Engineering"]:
            teamMembers = list(userCollection.find({"Position": userPosition}))
            # director = userCollection.find_one({"Dept": userDepartment, "Role": "Director"})
            # if director:
            #     teamMembers.append(director)
        else:
            teamMembers = list(userCollection.find({"Dept": userDepartment, "Position": userPosition})) 
        
        teamMembersDict = {member['Staff_ID']: member['Staff_FName'] + " " + member['Staff_LName'] for member in teamMembers}
        
        teamRequests = [] 
        for member in teamMembers:
            member_requests = list(requestsCollection.find({"Staff_ID": member['Staff_ID'], "Apply_Date": date}))
            teamRequests.extend(member_requests)  # Add member's requests to the list


        for teamRequest in teamRequests:  
            currMemberID = teamRequest['Staff_ID']
            currMemberName = teamMembersDict[currMemberID]
            wfh.append({ "name": currMemberName, "id": currMemberID, "type": teamRequest['Duration'], "status": teamRequest['Status'] })
            wfh_ids.add(currMemberID)

        for member in teamMembers:
            if member['Staff_ID'] not in wfh_ids:
                inOffice.append({ "name": teamMembersDict[member['Staff_ID']], "type": "Full Day", "id": member['Staff_ID'] })

        return jsonify({ "wfh": wfh, "inOffice": inOffice }), 200
    elif userRole == 1:
        ## Get all members in the organization
        allMembers = list(userCollection.find({}))
        allMembersDict = {member['Staff_ID']: member['Staff_FName'] + " " + member['Staff_LName'] for member in allMembers}
        allMembersDeptDict = {member['Staff_ID']: member['Dept'] for member in allMembers}

        ## Get all requests for the day
        allRequests = list(requestsCollection.find({"Apply_Date": date}))


        for singleRequest in allRequests:
            currMemberID = singleRequest['Staff_ID']
            currMemberName = allMembersDict[currMemberID]
            wfh.append({ "name": currMemberName, "id": currMemberID, "type": singleRequest['Duration'], "status": singleRequest['Status'], "department": allMembersDeptDict[currMemberID] })
            wfh_ids.add(currMemberID)

        
        for member in allMembers:
            if member['Staff_ID'] not in wfh_ids:
                inOffice.append({ "name": allMembersDict[member['Staff_ID']], "type": "Full Day", "id": member['Staff_ID'], "department": member['Dept'] })

        return jsonify({ "wfh": wfh, "inOffice": inOffice }), 200
    elif userRole == 3:
        ## Get all members within that department
        allMembers = list(userCollection.find({"Dept": userDepartment}))
        ## Remove the user with the role 'Director' from the list
        allMembers = [member for member in allMembers if member['Position'] != 'Director']
        allMembersDict = {member['Staff_ID']: member['Staff_FName'] + " " + member['Staff_LName'] for member in allMembers}

        ## Get all requests for the day
        allRequests = list(requestsCollection.find({"Apply_Date": date}))

        for singleRequest in allRequests:
            currMemberID = singleRequest['Staff_ID']
            currMemberName = allMembersDict[currMemberID]
            wfh.append({ "name": currMemberName, "id": currMemberID, "type": singleRequest['Duration'], "status": singleRequest['Status'] })
            wfh_ids.add(currMemberID)

        
        for member in allMembers:
            if member['Staff_ID'] not in wfh_ids:
                inOffice.append({ "name": allMembersDict[member['Staff_ID']], "type": "Full Day", "id": member['Staff_ID'] })

        return jsonify({ "wfh": wfh, "inOffice": inOffice }), 200
    


if __name__ == '__main__':
    app.run(debug=True)
