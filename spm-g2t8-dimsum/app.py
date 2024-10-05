from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from database.counter import get_next_sequence_value


app = Flask(__name__)


connection_string = "mongodb+srv://wxlum2022:PbQciwo6xIcw0eqt@assignment.9wecd.mongodb.net/"

app.secret_key = 'your_secret_key'

client = MongoClient(connection_string)
db = client['NewAssignment'] 
collection = db['NewAssignment']  


# Route for the login page
@app.route('/')
def login():
    return render_template('login.html')

# Route to handle login submission
@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form['email']
    password = request.form['password']

    # Query the MongoDB collection to verify the email and Staff_ID (password)
    user = collection.find_one({"Email": email, "Staff_ID": int(password)})

    if user:
        flash(f"Welcome {user['Staff_FName']}!", "success")
        return redirect(url_for('helloword'))
    else:
        flash("Invalid email or password. Please try again.", "danger")
        return redirect(url_for('login'))
    
@app.route('/helloword')
def helloword():
    return render_template('helloword.html')


@app.route('/testing')
def testing():
    return render_template('testing.html')


# processing WFH request form
@app.route('/process_request', methods=['POST'])
def process():
    staff_ID = int(request.form['staffID'])
    start_date = request.form['startDate']
    start_am_pm = request.form['startAmPm']
    end_date = request.form['endDate']
    end_am_pm = request.form['endAmPm']

    # - need to grab employee info that is passed over from form !!!!! - to get employee ID + manager ID

    # Convert date strings into datetime objects
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    # Create a list of dictionaries to store dates and their corresponding duration
    results = []

    # Case 1: If start and end date are the same day
    if start_date_obj == end_date_obj:
        if start_am_pm == 'AM' and end_am_pm == 'PM':
            # If it starts in the morning and ends in the evening, mark it as Full Day
            results.append({
                'date': start_date_obj.strftime('%d %B %Y'),
                'duration': 'Full Day'
            })
        else:
            # If it only spans AM or PM, mark it accordingly
            results.append({
                'date': start_date_obj.strftime('%d %B %Y'),
                'duration': start_am_pm
            })

    else:
        # Case 2: If start and end dates are different
        # Handle the start date
        if start_am_pm == 'AM':
            results.append({
                'date': start_date_obj.strftime('%d %B %Y'),
                'duration': 'Full Day'
            })
        else:
            results.append({
                'date': start_date_obj.strftime('%d %B %Y'),
                'duration': 'PM'
            })

        # Handle intermediate dates
        current_date = start_date_obj + timedelta(days=1)
        while current_date < end_date_obj:
            results.append({
                'date': current_date.strftime('%d %B %Y'),
                'duration': 'Full Day'
            })
            current_date += timedelta(days=1)

        # Handle the end date
        if end_am_pm == 'PM':
            results.append({
                'date': end_date_obj.strftime('%d %B %Y'),
                'duration': 'Full Day'
            })
        else:
            results.append({
                'date': end_date_obj.strftime('%d %B %Y'),
                'duration': 'AM'
            })
        
    
    # Connect to database
    connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
    client = MongoClient(connection_string)
    db = client['Arrangement']
    clashing_records = []

    # Check database for duplicates
    for day in results:
        date = day['date']
        duration = day['duration']

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

        existing_record = db["Arrangement"].find_one(check_clash_query)

        if existing_record:    
            clashing_records.append(existing_record)
            print(existing_record)

    # If any clash records exist, prepare a message
    if clashing_records:
        clash_messages = []
        for record in clashing_records:
            clash_date = record["Apply_Date"]  # Assuming 'Date' field exists in the record
            clash_duration = record["Duration"]
            clash_messages.append(f"Clash found for {clash_date} with duration {clash_duration}.")

        # Flash all clash messages
        for msg in clash_messages:
            flash(msg)

        return redirect(url_for('testing'))
        

        # existing_record = db["Arrangement"].find_one(check_clash_query)

        # if existing_record:
        #     flash(f"There is a clash for {date} with duration {duration}.")
        #     return redirect(url_for('testing'))

    # Get unique request_ID for this request
    request_id = get_next_sequence_value("request_id")

    for day in results:
        date = day['date']
        duration = day['duration']

        request_data = {
            "Request_ID": request_id,
            "Staff_ID": staff_ID,
            "Request_Date": datetime.now(),  # Proper datetime object
            "Apply_Date": date,
            "Duration": duration,
            "Manager_ID": 5001,
            "Status": "Pending",
        }

        try:
            db['Arrangement'].insert_one(request_data)
            print("request inserted.")
            
        except Exception as e:
            print(f"Insert error: {e}")
            flash(f"Error in putting in DB")
            return redirect(url_for('testing'))

    flash(f"Request processed successfully."), 200  
    return redirect(url_for('testing'))
    


if __name__ == '__main__':
    app.run(debug=True)