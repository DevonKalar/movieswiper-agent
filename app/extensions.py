from pymongo import MongoClient

mongo_client: MongoClient | None = None
mongo_db = None

def init_mongo(app):
    global mongo_client, mongo_db
    mongo_client = MongoClient(app.config["MONGO_URI"])
    mongo_db = mongo_client.get_default_database()
