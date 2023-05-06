from pymongo import MongoClient
from pymongo.collection import Collection

client = MongoClient("mongodb://localhost:27017/")
db = client["vktotg"]
collection_users: Collection = db["users"]
