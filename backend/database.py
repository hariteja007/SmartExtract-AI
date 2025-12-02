from pymongo import MongoClient

# Adjust if your Mongo runs elsewhere
client = MongoClient("mongodb://localhost:27017/")

db = client["doc_extract_db"]
documents_collection = db["documents"]
