import pytest
import json
from flask import Flask, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
import unittest
import flask_testing
from datetime import datetime
from pymongo import MongoClient


# MongoDB connection string - replace with your actual connection string
class TestApp(flask_testing.TestCase):
    app = Flask(__name__)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"

    app.secret_key = 'your_secret_key'

    def client():
        global app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def mongo_client():
        global connection_string
        client = MongoClient(connection_string)
        yield client
        client.close()

    def setup_test_data(mongo_client):
        db = mongo_client['NewAssignment']      
        user_collection = db['NewAssignment']
        requests_db = mongo_client['Arrangement']
        result = requests_db['Arrangement'].delete_many({"Apply_Date": "11 November 2024"})


class TestCreateConsultation(TestApp):
    def test_non_json_request(client):
        response = client.post('/api/getSchedule', 
                            data='This is not JSON',
                            content_type='text/plain')
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Request must be in JSON format"}

    def test_missing_uid_or_date(client):
        response = client.post('/api/getSchedule', 
                            data=json.dumps({"uid": 210042}),
                            content_type='application/json')
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Missing 'uid' or 'date' in request body"}

    def test_invalid_date_format(client):
        response = client.post('/api/getSchedule', 
                            data=json.dumps({"uid": 210042, "date": "20241111"}),
                            content_type='application/json')
        assert response.status_code == 400
        assert "error" in json.loads(response.data)

    def test_user_not_found(client, setup_test_data):
        response = client.post('/api/getSchedule', 
                            data=json.dumps({"uid": 999, "date": "2024-11-11"}),
                            content_type='application/json')
        assert response.status_code == 404
        assert json.loads(response.data) == {"error": "User not found"}

