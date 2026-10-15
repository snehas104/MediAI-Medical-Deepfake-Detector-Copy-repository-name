
import os
from pymongo import MongoClient

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client["medi_ai"]

users_collection = db["users"]
scans_collection = db["scans"]
users_collection.create_index("email", unique=True)


def check_database_connection():
    """Check whether MongoDB is reachable."""
    client.admin.command("ping")
    return True