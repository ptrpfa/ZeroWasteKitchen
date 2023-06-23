import redis
from decouple import config
from pymongo import MongoClient

# Function to get MongoDB client
def get_mongodb():
    client = MongoClient(config('MONGODB_URI'))
    db_conn = client[config('MONGODB_NAME')]
    return client, db_conn

# Function to get Redis client
def get_redis():
    return redis.Redis(host=config('REDIS_HOST'), port=config('REDIS_PORT'), password=config('REDIS_PASSWORD'), decode_responses=True)