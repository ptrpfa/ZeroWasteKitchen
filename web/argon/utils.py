from decouple import config
from pymongo import MongoClient

# Function to get MongoDB database connection
def get_mongodb():
    client = MongoClient(config('MONGODB_URI'))
    return client[config('MONGODB_NAME')]

# Function to get MongoDB collections
def get_collection(name=''):
    db_conn = get_mongodb()
    if(name.lower() == 'instructions'):
        return db_conn['Instructions']
    elif(name.lower() == 'reviews'):
        return db_conn['Reviews']
    elif(name.lower() == 'nutrition'):
        return db_conn['Nutrition']
    else:
        return { "Instructions": db_conn['Instructions'], "Reviews": db_conn['Reviews'], "Nutrition": db_conn['Nutrition'] }
