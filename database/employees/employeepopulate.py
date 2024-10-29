import pandas as pd
from pymongo import MongoClient

# MongoDB connection details
connection_string = "mongodb+srv://wxlum2022:WHG1u7Ziy7dqh8oo@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Specify your database and collection
db = client['Users']  # Replace with your database name
collection = db['Users']  # Replace with your collection name

# Path to the CSV file
csv_file_path = 'employeenew.csv'

# Read CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Convert DataFrame to a list of dictionaries
data = df.to_dict(orient='records')

# Insert data into the MongoDB collection
try:
    result = collection.insert_many(data)
    print(f"Inserted {len(result.inserted_ids)} documents into the collection.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    client.close()  # Close the MongoDB connection
