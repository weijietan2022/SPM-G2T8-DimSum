from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient


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

if __name__ == '__main__':
    app.run(debug=True)