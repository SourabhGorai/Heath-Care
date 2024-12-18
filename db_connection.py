import pymongo

def get_db_connection():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client['Hospital_Management']

    return db