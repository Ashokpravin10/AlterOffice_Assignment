from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["user_database"]
cohort_collection = db["cohort"]

# Query the collection
cookie = "ashokpravin10"
user = cohort_collection.find_one({"data.cookie": cookie}, {"_id": 0})

if user:
    print("✅ User found:", user)
else:
    print("❌ No user found with this cookie.")
