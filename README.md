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

# Marketing Analytics Model
## Overview
The **Marketing Analytics Model** processes user data stored in MongoDB, segments users dynamically, and visualizes insights based on demographics, interests, and income levels. It supports:
- User segmentation based on location, demographics, and interests.
- Dynamic cohort updates as new data is ingested.
- Machine Learning (ML)-based clustering.
- Scalable data ingestion and transformation.

## Installation
Ensure you have the required dependencies:
```bash
pip install pymongo pandas seaborn matplotlib scikit-learn
```

## Database Schema
**MongoDB Collections:**
1. **unique** - Stores raw user data.
2. **cohort** - Stores segmented users based on defined rules and ML models.

### Sample Document Structure (unique Collection)
```json
{
  "data": {
    "created_at": "2024-03-01T12:30:45",
    "location": {
      "city": "New York",
      "country": "USA"
    },
    "demographics": {
      "age": 29,
      "gender": "Male",
      "income": "High"
    },
    "interests": ["Tech", "Finance"]
  }
}
```

## Data Processing & Segmentation

### 1. Fetch Data from MongoDB
```python
from pymongo import MongoClient
import pandas as pd

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["user_database"]
unique_collection = db["unique"]

cursor = unique_collection.find({}, {"_id": 0})
data = list(cursor)
df = pd.json_normalize(data)
df.head()
```

### 2. Data Cleaning & Transformation
```python
import numpy as np

df['data.created_at'] = pd.to_datetime(df['data.created_at'], errors='coerce')
df.fillna({'data.location.city': 'Unknown', 'data.demographics.income': 'Unknown'}, inplace=True)
df.info()
```

### 3. Data Visualization
#### User Distribution by Country
```python
import seaborn as sns
import matplotlib.pyplot as plt

location_counts = df['data.location.country'].value_counts()
plt.figure(figsize=(12,6))
sns.barplot(x=location_counts.index, y=location_counts.values, palette="viridis")
plt.xticks(rotation=45)
plt.title("User Distribution by Country")
plt.xlabel("Country")
plt.ylabel("User Count")
plt.show()
```

#### Age & Gender Distribution
```python
sns.histplot(df['data.demographics.age'].dropna(), bins=20, kde=True, color='blue')
plt.title("Age Distribution of Users")
plt.xlabel("Age")
plt.ylabel("Count")
plt.show()

sns.countplot(y=df['data.demographics.gender'], palette='coolwarm')
plt.title("User Distribution by Gender")
plt.show()
```

## Cohort Collection (Segmented Users)
### 1. Interest-Based Segmentation
```python
from collections import Counter

interests = df['data.interests'].dropna().explode()
interest_counts = Counter(interests)
interest_df = pd.DataFrame(interest_counts.items(), columns=["Interest", "Count"]).sort_values(by="Count", ascending=False)

plt.figure(figsize=(12,6))
sns.barplot(x="Count", y="Interest", data=interest_df, palette="magma")
plt.title("Top User Interests")
plt.xlabel("User Count")
plt.ylabel("Interests")
plt.show()
```

### 2. ML-Based Clustering
#### K-Means Clustering on Age Data
```python
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

features = df[['data.demographics.age']].dropna()
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=3, random_state=42)
df.loc[features.index, 'Cluster'] = kmeans.fit_predict(scaled_features)
```

#### Visualization of Clusters
```python
plt.figure(figsize=(10,6))
sns.scatterplot(x=df.loc[features.index, 'data.demographics.age'], y=df.loc[features.index, 'Cluster'], hue=df.loc[features.index, 'Cluster'], palette="Set2")
plt.title("User Clusters Based on Age")
plt.xlabel("Age")
plt.ylabel("Cluster")
plt.xlim(0, 100)
plt.show()
```

### 3. Cohort Assignment Based on Interests
```python
interest_categories = {
    "Sports": ["sports", "football", "basketball", "cricket", "tennis"],
    "Tech": ["tech", "ai", "gadgets", "programming", "blockchain"],
    "Movies": ["movies", "hollywood", "bollywood", "action", "drama"],
    "Finance": ["finance", "stock market", "investment", "banking", "crypto"]
}

def assign_cohort(interests):
    if isinstance(interests, float) or interests is None:
        return "Other"  
    interests = [i.lower().strip() for i in interests]
    for category, keywords in interest_categories.items():
        if any(interest in keywords for interest in interests):
            return category
    return "Other"

df["Cohort"] = df["data.interests"].apply(assign_cohort)
```

### 4. Cohort Visualization
```python
cohort_counts = df["Cohort"].value_counts()
plt.figure(figsize=(8, 5))
sns.barplot(y=cohort_counts.index, x=cohort_counts.values, palette="viridis")
plt.xlabel("User Count")
plt.ylabel("Cohort")
plt.title("User Cohort Distribution by Interests")
plt.show()
```

## Conclusion
This **Marketing Analytics Model** enables:
- **Dynamic Cohort Segmentation** based on real-time data.
- **Scalable Processing** for high-volume user data.
- **ML-driven Insights** for targeted marketing strategies.

### Future Enhancements
- Incorporate **Deep Learning** for advanced segmentation.
- Deploy **real-time updates** using Apache Kafka.
- Integrate **automated reporting** dashboards.


