from decouple import config
from pymongo import MongoClient

# Function to get MongoDB client
def get_mongodb():
    client = MongoClient(config('MONGODB_URI'))
    db_conn = client[config('MONGODB_NAME')]
    return client, db_conn