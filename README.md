# AlterOffice_Assignment

## 🚀 Project Overview
This project builds a **Marketing Analytics Model** using **MongoDB**, **FastAPI**, and **Python** to process, segment, and analyze user data based on **demographics, location, and interests**. It supports **real-time ingestion, cohort tracking, and segmentation** with scalable and high-performance data handling.

---
## 📌 Features
- **Data Ingestion**: Uploads raw CSV data to MongoDB (`users` collection).
- **Unique User Management**: Deduplicates users based on `cookie ID` and `email`.
- **Cohort Tracking**: Stores and updates users with repeated email IDs.
- **API Integration**: Provides REST API endpoints for data ingestion and retrieval.
- **User Segmentation**: Filters users dynamically based on demographics and interests.

---
## 🛠️ Installation & Setup
### 1️⃣ Install Required Libraries
```bash
pip install pandas pymongo fastapi uvicorn
```

### 2️⃣ Setup MongoDB
Ensure MongoDB is installed and running locally:
```bash
mongod --dbpath /path/to/data/directory
```

### 3️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/marketing-analytics.git
cd marketing-analytics
```

### 4️⃣ Configure MongoDB Connection
Update `MONGO_URI` in the Python scripts if needed (default is `mongodb://localhost:27017/`).

### 5️⃣ Run the FastAPI Server
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

---
## 📂 Data Processing Workflow
1. **Upload Data** using `upload_csv.py` into `users` collection.
2. **Process Unique Users**: Deduplicates users based on `cookie ID` and updates repeated emails.
3. **Segment Cohorts**: Users with repeated email IDs are stored separately.
4. **Serve APIs**: Fetch user details dynamically using FastAPI.

---
## 🚀 API Endpoints
### ✅ 1. Ingest User Data
**POST** `/api/ingest`
```json
{
  "data": {
    "cookie": "user_cookie_id",
    "email": "user@example.com",
    "phone_number": "1234567890",
    "created_at": "03/10/2025 15:30",
    "location": {
      "state": "California",
      "country": "USA",
      "city": "Los Angeles"
    },
    "demographics": {
      "age": 25,
      "gender": "Male",
      "income": "50000",
      "education": "Bachelor's"
    },
    "interests": ["Tech", "Gaming"]
  }
}
```

### ✅ 2. Get Unique User Data
**GET** `/api/user?cookie={cookie_id}`
```json
{
  "data": {
    "cookie": "user_cookie_id",
    "email": "user@example.com",
    "location": {"country": "USA", "city": "Los Angeles"},
    "demographics": {"age": 25, "gender": "Male"},
    "interests": ["Tech", "Gaming"]
  }
}
```

### ✅ 3. Get Cohort Users (Segmented Data)
**GET** `/api/cohort/user?cookie={cookie_id}&age_min=20&age_max=30&interests=Gaming`
```json
[
  {
    "data": {
      "cookie": "user_cookie_id",
      "email": "user@example.com",
      "location": {"country": "USA", "city": "Los Angeles"},
      "demographics": {"age": 25, "gender": "Male"},
      "interests": ["Tech", "Gaming"]
    }
  }
]
```

---
## 📊 Data Storage Schema
### 📌 `users` Collection (Raw Data)
```json
{
  "data": {
    "cookie": "user_cookie_id",
    "email": "user@example.com",
    "phone_number": "1234567890",
    "created_at": "2025-03-10T15:30:00",
    "location": {"state": "California", "country": "USA", "city": "Los Angeles"},
    "demographics": {"age": 25, "gender": "Male", "income": "50000", "education": "Bachelor's"},
    "interests": ["Tech", "Gaming"]
  }
}
```

### 📌 `unique` Collection (Deduplicated Users)
- Stores **one record per unique user**, updating details if email or cookie match.

### 📌 `cohort` Collection (Segmented Users)
- Stores **users with repeated email IDs** separately for segmentation.
