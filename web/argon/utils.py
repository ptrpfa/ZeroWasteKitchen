from decouple import config
from pymongo import MongoClient

# Function to get MongoDB database connection
def get_mongodb():
    return MongoClient(config('MONGODB_URI'))

# Function to get MongoDB collections
def get_collection(name=''):
    mongo_client = get_mongodb()
    db_conn = mongo_client[config('MONGODB_NAME')]
    results = None
    if(name.lower() == 'instructions'):
        results = db_conn['Instructions']
    elif(name.lower() == 'reviews'):
        results = db_conn['Reviews']
    elif(name.lower() == 'nutrition'):
        results = db_conn['Nutrition']
    else:
        results = { "Instructions": db_conn['Instructions'], "Reviews": db_conn['Reviews'], "Nutrition": db_conn['Nutrition'] }
    mongo_client.close()
    return results