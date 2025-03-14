import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List, Dict
import math

app = FastAPI()

# ✅ MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["user_database"]

# Collections
users_collection = db["users"]       # Raw insertion (no transformations)
unique_collection = db["unique"]     # Unique user data (one record per cookie)
cohort_collection = db["cohort"]     # Tracks updated users (merged email records)

# ✅ Function: Sanitize Data (Convert NaN to None)
def sanitize_data(data):
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(v) for v in data]
    elif isinstance(data, float) and math.isnan(data):
        return None
    return data

# ✅ Insert CSV Data (Only to "users")
def insert_csv_to_users(csv_path):
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient="records")

    formatted_records = []
    for record in records:
        # Convert created_at to datetime
        if "created_at" in record and pd.notna(record["created_at"]):
            record["created_at"] = datetime.strptime(str(record["created_at"]), "%m/%d/%Y %H:%M")

        # Ensure interests are stored as an array
        if "interests" in record and pd.notna(record["interests"]):
            record["interests"] = [interest.strip() for interest in record["interests"].split("|")]

        # Format for MongoDB
        formatted_record = {"data": record}
        formatted_records.append(formatted_record)

    # Insert into "users" collection (Raw Data)
    if formatted_records:
        users_collection.insert_many(formatted_records)
        print("✅ CSV Data Successfully Inserted into MongoDB!")
    else:
        print("⚠️ No valid records found to insert.")

# ✅ Insert or Update Unique & Cohort Users
@app.post("/api/ingest")
def insert_user(payload: Dict):
    if "data" not in payload or "cookie" not in payload["data"] or "email" not in payload["data"]:
        raise HTTPException(status_code=400, detail="Missing required fields in 'data'")

    data = sanitize_data(payload["data"])  # Sanitize input
    cookie = data["cookie"]
    email = data["email"]

    # ✅ Ensure created_at is handled properly
    if "created_at" in data and isinstance(data["created_at"], str):
        try:
            data["created_at"] = datetime.strptime(data["created_at"], "%m/%d/%Y %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for created_at")

    # ✅ 1. Insert into "users" (Raw Data - No transformation)
    users_collection.insert_one({"data": data})

    # ✅ 2. Check if user exists in "unique" (by cookie or email)
    existing_cookie_user = unique_collection.find_one({"data.cookie": cookie})
    existing_email_user = unique_collection.find_one({"data.email": email})

    if existing_cookie_user:
        # ✅ Update Unique user by cookie (Merge & keep created_at)
        merged_data = {**existing_cookie_user["data"], **data}
        unique_collection.update_one({"data.cookie": cookie}, {"$set": {"data": merged_data}})
        return {"message": "User updated successfully in unique table"}

    elif existing_email_user:
        # ✅ Merge Email (Keep latest cookie but retain previous created_at)
        merged_data = {**existing_email_user["data"], **data}
        merged_data["created_at"] = existing_email_user["data"].get("created_at", data.get("created_at"))

        unique_collection.update_one({"data.email": email}, {"$set": {"data": merged_data}})
        cohort_collection.insert_one({"data": merged_data})
        return {"message": "User email matched, merged profile in unique and stored in cohort"}

    else:
        # ✅ Insert as a new user into "unique" table
        unique_collection.insert_one({"data": data})
        return {"message": "New user inserted successfully in unique table"}

# ✅ Retrieve User by Email or Cookie (From Unique Table)
@app.get("/api/user")
def get_user(email: Optional[str] = None, cookie: Optional[str] = None):
    if not email and not cookie:
        raise HTTPException(status_code=400, detail="Provide either 'email' or 'cookie'")

    query = {"data.email": email} if email else {"data.cookie": cookie}
    user = unique_collection.find_one(query, {"_id": 0})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return sanitize_data(user)

# ✅ Retrieve Cohort Users (Filtered Search)
@app.get("/api/cohort/user")
def get_cohort_users(
    cookie: Optional[str] = None,
    email: Optional[str] = None,
    country: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    gender: Optional[str] = None,
    income: Optional[str] = None,
    education: Optional[str] = None,
    interests: Optional[List[str]] = Query(None)
):
    query = {}

    if cookie:
        query["data.cookie"] = cookie
    if email:
        query["data.email"] = email
    if country:
        query["data.location.country"] = country
    if age_min:
        query["data.demographics.age"] = {"$gte": age_min}
    if age_max:
        query.setdefault("data.demographics.age", {})["$lte"] = age_max
    if gender:
        query["data.demographics.gender"] = gender
    if income:
        query["data.demographics.income"] = income
    if education:
        query["data.demographics.education"] = education
    if interests:
        query["data.interests"] = {"$in": interests}

    users = list(cohort_collection.find(query, {"_id": 0}))

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    return sanitize_data(users)

# ✅ Health Check Endpoint
@app.get("/api/health")
def health_check():
    return {"status": "OK"}