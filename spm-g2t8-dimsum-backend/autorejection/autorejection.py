import pymongo
from datetime import datetime, timedelta
import requests

# MongoDB connection setup
connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"
client = pymongo.MongoClient(connection_string)
requests_db = client["Arrangement"]
requests_collection = requests_db["Arrangement"]

rejection_db = client["Rejection"]
rejection_collection = rejection_db["Rejection"]

users_db = client["NewAssignment"]
users_collection = users_db["NewAssignment"]


## Rejection Collection Class
class Rejected_Request:
    def __init__(self, request_id, staff_id, request_date, apply_date, duration, manager_id, reason, reject_date_time):
        self.Request_id = request_id
        self.Staff_id = staff_id
        self.Request_date = request_date
        self.Apply_date = apply_date
        self.Duration = duration
        self.Manager_id = manager_id
        self.Reason = reason
        self.Reject_date_time = reject_date_time

    def insert_rejected_request(self):
        rejection_collection.insert_one({
            "Request_ID": self.Request_id,
            "Staff_ID": self.Staff_id,
            "Request_Date": self.Request_date,
            "Apply_Date": self.Apply_date,
            "Duration": self.Duration,
            "Manager_ID": self.Manager_id,
            "Reason": self.Reason,
            "Reject_Date_Time": self.Reject_date_time
        })


def update_requests():
    # Get the current day of the week (0 = Monday, 4 = Friday)
    current_day = datetime.now().weekday()

    ## for now, simulate current date to be friday (yesterday)
    current_date = datetime.now()

    if current_day in range(0, 4):  # Monday to Thursday (0-3)
        # Retrieve all requests with a specific date and update their status to "rejected"
        next_day = (current_date + timedelta(days=1)).strftime("%d %B %Y")
        print(next_day)
        
    elif current_day == 4:  # Friday
        # Calculate the next Monday's date
        next_day = (current_date + timedelta(days=3)).strftime("%d %B %Y")
        print(next_day)
        


    # Retrieve all the requests for that day that are PENDING
    relevant_requests = list(requests_collection.find({"Apply_Date": next_day, "Status": "Pending"}))

    # Update the requests status to "Rejected"
    requests_collection.update_many(
        {"Apply_Date": next_day},
        {"$set": {"Status": "Rejected"}}
    )

    # Insert the rejected requests into the rejected collection
    # And send a notification to the staff
    for request in relevant_requests:
        rejected_request = Rejected_Request(
            request["Request_ID"],
            request["Staff_ID"],
            request["Request_Date"],
            request["Apply_Date"],
            request["Duration"],
            0,
            "Automated Rejection - The request was not approved or rejected prior to 24 hours before the request date.",
            datetime.now()
        )

        rejected_request.insert_rejected_request()

        # Retrieve the staff's email
        staff = users_collection.find_one({"Staff_ID": request["Staff_ID"]})
        email = staff["Email"]
        fullName = staff["Staff_FName"] + " " + staff["Staff_LName"]

        # Send notification to the staff
        response = requests.post("http://localhost:5003/api/sendAutomaticRejectionNotification", json={
            "email": email,
            "name": fullName,
            "requestId": request["Request_ID"],
            "date": request["Apply_Date"],
            "type": request["Duration"]
        })

        if response.status_code == 200:
            print(f"Notification sent to {email} successfully.")
        else:
            print(f"Failed to send notification to {email}.")


if __name__ == "__main__":
    update_requests()
