import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["user_database"]
users_collection = db["users"]
unique_collection = db["unique"]
cohort_collection = db["cohort"]

# ✅ Insert CSV Data (Only to "users")
def insert_csv_to_users(csv_path):
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient="records")

    formatted_records = []
    for record in records:
        # Convert created_at to datetime
        if "created_at" in record and pd.notna(record["created_at"]):
            try:
                record["created_at"] = datetime.strptime(str(record["created_at"]), "%m/%d/%Y %H:%M")
            except ValueError:
                print(f"⚠️ Invalid date format for record: {record}")
                continue  # Skip invalid date format records

        # Ensure interests are stored as an array
        if "interests" in record and pd.notna(record["interests"]):
            record["interests"] = [interest.strip() for interest in record["interests"].split("|")]

        # Format for MongoDB
        formatted_record = {"data": record}
        formatted_records.append(formatted_record)

    # Insert into "users" collection (Raw Data)
    if formatted_records:
        users_collection.insert_many(formatted_records)
        print("✅ CSV Data Successfully Inserted into 'users' Collection!")
    else:
        print("⚠️ No valid records found to insert.")

# ✅ Insert or Update Unique & Cohort Users (Including `created_at`)
def insert_to_unique_and_cohort(csv_path):
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient="records")

    for record in records:
        # Convert created_at to datetime
        if "created_at" in record and pd.notna(record["created_at"]):
            try:
                record["created_at"] = datetime.strptime(str(record["created_at"]), "%m/%d/%Y %H:%M")
            except ValueError:
                print(f"⚠️ Skipping record due to invalid date format: {record}")
                continue

        # Ensure interests are stored as an array
        if "interests" in record and pd.notna(record["interests"]):
            record["interests"] = [interest.strip() for interest in record["interests"].split("|")]

        # Extract important details
        cookie = record.get("cookie", "").strip()
        email = record.get("email", "").strip()

        if not cookie or not email:
            continue  # Skip records missing required fields

        formatted_record = {
            "data": {
                "cookie": cookie,
                "email": email,
                "phone_number": record.get("phone_number", ""),
                "created_at": record.get("created_at"),  # ✅ Ensure `created_at` is included
                "location": {
                    "state": record.get("state", ""),
                    "country": record.get("country", ""),
                    "city": record.get("city", "")
                },
                "demographics": {
                    "age": record.get("age", None),
                    "gender": record.get("gender", ""),
                    "income": record.get("income", ""),
                    "education": record.get("education", "")
                },
                "interests": record.get("interests", [])
            }
        }

        # ✅ Check if user exists in "unique" (by cookie)
        existing_cookie_user = unique_collection.find_one({"data.cookie": cookie})
        existing_email_user = unique_collection.find_one({"data.email": email})

        if existing_cookie_user:
            # ✅ Update Unique user by cookie (Keep all previous data and update new fields)
            merged_data = {**existing_cookie_user["data"], **formatted_record["data"]}
            unique_collection.update_one({"data.cookie": cookie}, {"$set": {"data": merged_data}})
            print(f"🔄 Updated user with cookie: {cookie} in 'unique' collection")

        elif existing_email_user:
            # ✅ Merge Email (Keep latest cookie but retain previous data)
            merged_data = {**existing_email_user["data"], **formatted_record["data"]}
            merged_data["cookie"] = cookie  # Update cookie ID with latest

            # ✅ Update unique collection
            unique_collection.update_one({"data.email": email}, {"$set": {"data": merged_data}})
            
            # ✅ Store merged profile in "cohort"
            cohort_collection.insert_one({"data": merged_data})
            print(f"📌 Email match: {email}, merged profile stored in 'cohort' collection")

        else:
            # ✅ Insert as a new user into "unique" table
            unique_collection.insert_one(formatted_record)
            print(f"✅ Inserted new unique user: {email}")

# ✅ Retrieve User by Email or Cookie (From Unique Table)
def get_user(email=None, cookie=None):
    if not email and not cookie:
        return {"error": "Provide either 'email' or 'cookie'"}

    query = {"data.email": email} if email else {"data.cookie": cookie}
    user = unique_collection.find_one(query, {"_id": 0})

    if not user:
        return {"error": "User not found"}

    return user

# ✅ Retrieve Cohort Users (Filtered Search)
def get_cohort_users(cookie=None, email=None, country=None, age_min=None, age_max=None, gender=None, income=None, education=None, interests=None):
    query = {}

    if cookie:
        query["data.cookie"] = cookie
    if email:
        query["data.email"] = email
    if country:
        query["data.location.country"] = country
    if age_min is not None:
        query["data.demographics.age"] = {"$gte": age_min}
    if age_max is not None:
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
        return {"error": "No users found"}
    
    return users

# ✅ Run the script
if __name__ == "__main__":
    csv_path = r"D:\alter_office\sample_user_data.csv"

    print("\n📂 Importing data into 'users' collection...")
    insert_csv_to_users(csv_path)  # Insert raw CSV data into users

    print("\n🔍 Processing data for 'unique' and 'cohort' collections...")
    insert_to_unique_and_cohort(csv_path)  # Process data for unique & cohort

    print("\n✅ All operations completed successfully!")
