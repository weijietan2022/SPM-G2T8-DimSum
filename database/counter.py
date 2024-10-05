from pymongo import MongoClient

# Replace with your actual MongoDB Atlas connection string
connection_string = "mongodb+srv://jiaqinggui:jq2022@assignment.9wecd.mongodb.net/"
client = MongoClient(connection_string)

# Access the specific database
db = client['Arrangement']

# Create the counters collection if it doesn't exist
if "counters" not in db.list_collection_names():
    db.create_collection("counters")

# Initialize the Request_ID counter
if db['counters'].count_documents({"_id": "request_id"}) == 0:
    db['counters'].insert_one({
        "_id": "request_id",  # Unique identifier for the counter
        "sequence_value": 0   # Initial value of the counter
    })

    print("Counter created")

# Function to get the next sequence value
def get_next_sequence_value(sequence_name):
    # Find and update the counter for the given sequence name
    result = db['counters'].find_one_and_update(
        {"_id": sequence_name},   # The document where _id = sequence_name
        {"$inc": {"sequence_value": 1}},  # Increment the sequence_value by 1
        return_document=True     # Return the updated document after the increment
    )
    return result['sequence_value']  # Return the incremented sequence_value

# # Example usage: Inserting a new Request_ID
# request_id = get_next_sequence_value("request_id")
# print(f"Next Request_ID: {request_id}")