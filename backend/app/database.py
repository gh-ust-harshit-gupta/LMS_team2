from pymongo import MongoClient
from app import config

client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]


def get_db():
    return db
