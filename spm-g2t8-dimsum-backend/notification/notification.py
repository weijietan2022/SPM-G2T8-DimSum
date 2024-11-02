from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import smtplib
from dotenv import load_dotenv
from pathlib import Path
import os

app = Flask(__name__)

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
app.secret_key = os.getenv("SECRET_KEY")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv("EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
mail = Mail(app)

@app.route("/api/sendApprovalNotification", methods=['POST'])
def sendNotification():
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    data = request.json

    if 'email' not in data or 'name' not in data or 'requestId' not in data or 'date' not in data or 'type' not in data:
        return jsonify({"error": "Missing information in request body"}), 404
    
    email = data['email']
    name = data['name']
    requestId = data['requestId']
    date = data['date']
    type = data['type']
    
    msg = Message(
        subject="Outcome of WFH Request",
        sender="spmdimsum@gmail.com",
        recipients=[email],
        body=f"Dear {name},\n\nYour WFH request with ID {requestId} for {date}, {type} has been approved by your manager.\n\nThis is an automated email from the system. Please do not reply. \n\nThank you."
    )
    
    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return jsonify({"error": "Failed to send email", "details": str(e)}), 500



@app.route("/api/sendRejectionNotification", methods=['POST'])
def sendRejectionNotification():

    print("Triggered")
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    data = request.json

    if 'email' not in data or 'name' not in data or 'requestId' not in data or 'date' not in data or 'type' not in data:
        return jsonify({"error": "Missing information in request body"}), 404
    
    email = data['email']
    name = data['name']
    requestId = data['requestId']
    date = data['date']
    type = data['type']
    
    print("Checks complete. ")
    msg = Message(
        subject="Outcome of WFH Request",
        sender="spmdimsum@gmail.com",
        recipients=[email],
        body=f"Dear {name},\n\nYour WFH request with ID {requestId} for {date}, {type} has been rejected by your manager. Please log into the system to see the details of your why your request was rejected.\n\nThis is an automated email from the system. Please do not reply. \n\nThank you.",
    )

    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return jsonify({"error": "Failed to send email", "details": str(e)}), 500
    

@app.route("/api/sendRequestNotification", methods=['POST'])
def sendRequestNotification():
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    data = request.json

    if 'managerEmail' not in data or 'managerName' not in data or 'name' not in data or 'requestId' not in data or 'dates' not in data or 'type' not in data:
        return jsonify({"error": "Missing information in request body"}), 404
    
    name = data['name']
    managerEmail = data['managerEmail']
    managerName = data['managerName']
    dates = data['dates']
    requestId = data['requestId']
    types = data['type']

    bodyE = f"Dear {managerName},\n\nA new WFH Request has been submitted by {name}. Please see details below:\n\nRequest ID: {requestId}\n"
    for i in range(len(dates)):
        bodyE += f"Date: {dates[i]}, Type: {types[i]}\n"

    bodyE += "\nThis is an automated email from the system. Please do not reply. \n\nThank you."

    msg = Message(
        subject="New WFH Request from Employee",
        sender="spmdimsum@gmail.com",
        recipients=[managerEmail],
        body=bodyE,
    )

    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return jsonify({"error": "Failed to send email", "details": str(e)}), 500

    
@app.route("/api/sendCancellationNotification", methods=['POST'])
def sendCancellationNotification():
    if not request.is_json:
        print("Request must be in JSON format")
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    data = request.json

    if 'managerEmail' not in data or 'managerName' not in data or 'name' not in data or 'requestId' not in data or 'date' not in data or 'type' not in data:
        return jsonify({"error": "Missing information in request body"}), 404
    
    name = data['name']
    managerEmail = data['managerEmail']
    managerName = data['managerName']
    requestId = data['requestId']
    date = data['date']
    type = data['type']
    
    msg = Message(
        subject="Outcome of WFH Request",
        sender="spmdimsum@gmail.com",
        recipients=[managerEmail],
        body=f"Dear {managerName},\n\nA WFH Request you had previously approved has been withdrawn. Please see details below:\n\nRequestor: {name}\nRequest ID: {requestId}\nDate: {date}\nType: {type}\n\nThis is an automated email from the system. Please do not reply. \n\nThank you.",
    )

    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return jsonify({"error": "Failed to send email", "details": str(e)}), 500
    
@app.route("/api/sendAutomaticRejectionNotification", methods=['POST'])
def sendAutomaticRejectionNotification():
    if not request.is_json:
        print("Request must be in JSON format")
        return jsonify({"error": "Request must be in JSON format"}), 400
    
    data = request.json

    if 'email' not in data or 'name' not in data or 'requestId' not in data or 'date' not in data or 'type' not in data:
        return jsonify({"error": "Missing information in request body"}), 404
    
    email = data['email']
    name = data['name']
    requestId = data['requestId']
    date = data['date']
    type = data['type']
    
    msg = Message(
        subject="Outcome of WFH Request",
        sender="spmdimsum@gmail.com",
        recipients=[email],
        body=f"Dear {name},\n\nYour WFH request with ID {requestId} for {date}, {type} has been rejected automatically, due to the 24-hour policy. \n\nThis is an automated email from the system. Please do not reply. \n\nThank you.",
    )

    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return jsonify({"error": "Failed to send email", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5003)