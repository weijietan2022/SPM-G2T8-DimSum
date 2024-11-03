import pymongo
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


# MongoDB connection setup
class RequestsDB:
    def __init__(self):
        connection_string = os.getenv("DB_CON_STRING")
        client = pymongo.MongoClient(connection_string)
        self.collection = client[os.getenv("DB_ARRANGEMENT")][os.getenv("COLLECTION_ARRANGEMENT")]

    def find_pending_requests(self, apply_date):
        return list(self.collection.find({"Apply_Date": apply_date, "Status": "Pending"}))

    def reject_requests(self, apply_date):
        self.collection.update_many(
            {"Apply_Date": apply_date},
            {"$set": {"Status": "Rejected"}}
        )


class RejectionDB:
    def __init__(self):
        connection_string = os.getenv("DB_CON_STRING")
        client = pymongo.MongoClient(connection_string)
        self.collection = client[os.getenv("DB_REJECTION")][os.getenv("COLLECTION_REJECTION")]

    def insert_rejected_request(self, rejected_request):
        self.collection.insert_one({
            "Request_ID": rejected_request.Request_id,
            "Staff_ID": rejected_request.Staff_id,
            "Request_Date": rejected_request.Request_date,
            "Apply_Date": rejected_request.Apply_date,
            "Duration": rejected_request.Duration,
            "Manager_ID": rejected_request.Manager_id,
            "Reason": rejected_request.Reason,
            "Reject_Date_Time": rejected_request.Reject_date_time
        })


class UsersDB:
    def __init__(self):
        connection_string = os.getenv("DB_CON_STRING")
        client = pymongo.MongoClient(connection_string)
        self.collection = client[os.getenv("DB_USERS")][os.getenv("COLLECTION_USERS")]

    def find_user_by_id(self, staff_id):
        return self.collection.find_one({"Staff_ID": staff_id})


class RejectedRequest:
    def __init__(self, request_id, staff_id, request_date, apply_date, duration, manager_id, reason, reject_date_time):
        self.Request_id = request_id
        self.Staff_id = staff_id
        self.Request_date = request_date
        self.Apply_date = apply_date
        self.Duration = duration
        self.Manager_id = manager_id
        self.Reason = reason
        self.Reject_date_time = reject_date_time

    def insert(self, rejection_db):
        rejection_db.insert_rejected_request(self)


def update_requests(requests_db, rejection_db, users_db):
    current_day = datetime.now().weekday()
    current_date = datetime.now()

    if current_day in range(0, 4):  # Monday to Thursday
        next_day = (current_date + timedelta(days=1)).strftime("%d %B %Y")
    elif current_day == 4:  # Friday
        next_day = (current_date + timedelta(days=3)).strftime("%d %B %Y")
    elif current_day == 5:  # Saturday
        next_day = (current_date + timedelta(days=2)).strftime("%d %B %Y")
    elif current_day == 6:  # Sunday
        next_day = (current_date + timedelta(days=1)).strftime("%d %B %Y")

    relevant_requests = requests_db.find_pending_requests(next_day)
    requests_db.reject_requests(next_day)

    numberOfRequests = len(relevant_requests)
    requestsUpdated = 0

    for request in relevant_requests:
        rejected_request = RejectedRequest(
            request["Request_ID"],
            request["Staff_ID"],
            request["Request_Date"],
            request["Apply_Date"],
            request["Duration"],
            0,
            "Automated Rejection - The request was not approved or rejected prior to 24 hours before the request date.",
            datetime.now()
        )
        rejected_request.insert(rejection_db)

        staff = users_db.find_user_by_id(request["Staff_ID"])
        email = staff["Email"]
        fullName = staff["Staff_FName"] + " " + staff["Staff_LName"]

        response = requests.post("http://localhost:5003/api/sendAutomaticRejectionNotification", json={
            "email": email,
            "name": fullName,
            "requestId": request["Request_ID"],
            "date": request["Apply_Date"],
            "type": request["Duration"]
        })

        if response.status_code == 200:
            requestsUpdated += 1
        else:
            print("Failed to send email to " + email)
    return {"requestsUpdated": requestsUpdated, "totalRequests": numberOfRequests}


if __name__ == "__main__":
    requests_db = RequestsDB()
    rejection_db = RejectionDB()
    users_db = UsersDB()
    update_requests(requests_db, rejection_db, users_db)
