#!/usr/bin/env python
# coding: utf-8

# In[20]:


pip install pymongo pandas seaborn matplotlib scikit-learn


# In[23]:


import pandas as pd
from pymongo import MongoClient

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["user_database"]
unique_collection = db["unique"]

# Fetch Data from MongoDB
cursor = unique_collection.find({}, {"_id": 0})  # Remove MongoDB's _id field
data = list(cursor)

# Convert to DataFrame
df = pd.json_normalize(data)

# Display first 5 rows
df.head()


# In[28]:


df.tail()


# In[25]:


import numpy as np

# Convert 'created_at' to datetime
df['data.created_at'] = pd.to_datetime(df['data.created_at'], errors='coerce')

# Fill missing values
df.fillna({'data.location.city': 'Unknown', 'data.demographics.income': 'Unknown'}, inplace=True)

# Display data types
df.info()


# In[29]:


import seaborn as sns
import matplotlib.pyplot as plt

# Count users per country
location_counts = df['data.location.country'].value_counts()

# Plot
plt.figure(figsize=(12,6))
sns.barplot(x=location_counts.index, y=location_counts.values, palette="viridis")
plt.xticks(rotation=45)
plt.title("User Distribution by Country")
plt.xlabel("Country")
plt.ylabel("User Count")
plt.show()


# In[30]:


# Age Distribution
plt.figure(figsize=(10,5))
sns.histplot(df['data.demographics.age'].dropna(), bins=20, kde=True, color='blue')
plt.title("Age Distribution of Users")
plt.xlabel("Age")
plt.ylabel("Count")
plt.show()


# In[31]:


# Gender Distribution
plt.figure(figsize=(8,5))
sns.countplot(y=df['data.demographics.gender'], palette='coolwarm')
plt.title("User Distribution by Gender")
plt.show()


# In[32]:


from collections import Counter

# Flatten interest lists
interests = df['data.interests'].dropna().explode()
interest_counts = Counter(interests)

# Convert to DataFrame
interest_df = pd.DataFrame(interest_counts.items(), columns=["Interest", "Count"]).sort_values(by="Count", ascending=False)

# Plot
plt.figure(figsize=(12,6))
sns.barplot(x="Count", y="Interest", data=interest_df, palette="magma")
plt.title("Top User Interests")
plt.xlabel("User Count")
plt.ylabel("Interests")
plt.show()


# In[33]:


from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Selecting relevant numeric features
features = df[['data.demographics.age']]
features = features.dropna()  # Remove missing values

# Scale Data
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Display first 5 rows
scaled_features[:5]


# In[42]:


# Apply K-Means
kmeans = KMeans(n_clusters=3, random_state=42)
df.loc[features.index, 'Cluster'] = kmeans.fit_predict(scaled_features)

# Display first 5 rows
df[['data.demographics.age', 'Cluster']].head()


# In[43]:


plt.figure(figsize=(10,6))
sns.scatterplot(x=df.loc[features.index, 'data.demographics.age'], y=df.loc[features.index, 'Cluster'], hue=df.loc[features.index, 'Cluster'], palette="Set2")
plt.title("User Clusters Based on Age")
plt.xlabel("Age")
plt.ylabel("Cluster")
plt.xlim(0, 100)
plt.show()


# In[44]:


# Count occurrences of each income group
plt.figure(figsize=(12,6))
sns.countplot(y=df["data.demographics.income"], order=df["data.demographics.income"].value_counts().index, palette="coolwarm")
plt.title("Income Distribution")
plt.xlabel("Count")
plt.ylabel("Income Range")
plt.show()


# In[45]:


plt.figure(figsize=(10,6))
sns.boxplot(y=df["data.demographics.income"], x=df["data.demographics.age"], palette="viridis")
plt.title("Income vs. Age Distribution")
plt.xlabel("Age")
plt.ylabel("Income Range")
plt.show()


# In[46]:


plt.figure(figsize=(8,5))
sns.countplot(y=df["data.demographics.income"], hue=df["data.demographics.gender"], palette="Set2")
plt.title("Income Distribution by Gender")
plt.ylabel("Income Range")
plt.xlabel("Count")
plt.legend(title="Gender")
plt.show()


# In[47]:


# Extract Interests
income_interests = df.explode("data.interests")

plt.figure(figsize=(12,6))
sns.countplot(y=income_interests["data.interests"], hue=income_interests["data.demographics.income"], palette="Spectral")
plt.title("Income Levels Across User Interests")
plt.xlabel("User Count")
plt.ylabel("Interests")
plt.legend(title="Income")
plt.show()


# In[61]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ✅ Sample DataFrame (Replace this with MongoDB Data)
data = [
    {"data": {"interests": ["Sports", "Tech", "Finance", "Travel"]}},
    {"data": {"interests": ["Movies", "Tech"]}},
    {"data": {"interests": ["Cricket", "Basketball"]}},
    {"data": {"interests": ["Stock Market", "Crypto"]}},
    {"data": {"interests": ["Tennis", "Gadgets"]}},
    {"data": {"interests": ["Investment", "Banking"]}},
    {"data": {"interests": ["Unknown Interest"]}},  # Should go to "Other"
]

df = pd.DataFrame(data)

# ✅ Extract Interests from 'data'
df["interests"] = df["data"].apply(lambda x: x.get("interests", []) if isinstance(x, dict) else [])

# ✅ Normalize Interests (Lowercase + Trim Spaces)
df["interests"] = df["interests"].apply(lambda x: [i.strip().lower() for i in x] if isinstance(x, list) else [])

# ✅ Print Unique Interests to Debug
unique_interests = set([interest for sublist in df["interests"] for interest in sublist])
print("🔹 Unique Interests in Data:", unique_interests)

# ✅ Define Interest Categories (Lowercased for Matching)
interest_categories = {
    "Sports": ["sports", "football", "basketball", "cricket", "tennis"],
    "Tech": ["tech", "ai", "gadgets", "programming", "blockchain"],
    "Movies": ["movies", "hollywood", "bollywood", "action", "drama"],
    "Finance": ["finance", "stock market", "investment", "banking", "crypto"]
}

# ✅ Assign Users to Segments
def assign_cohort(interests):
    for category, keywords in interest_categories.items():
        if any(interest in keywords for interest in interests):
            return category
    return "Other"

# ✅ Apply Cohort Assignment
df["Cohort"] = df["interests"].apply(assign_cohort)

# ✅ Count Users per Segment
cohort_counts = df["Cohort"].value_counts()

# ✅ Plot Cohort Distribution
plt.figure(figsize=(8, 5))
sns.barplot(y=cohort_counts.index, x=cohort_counts.values, palette="viridis")
plt.xlabel("User Count")
plt.ylabel("Cohort")
plt.title("User Cohort Distribution by Interests")
plt.show()

# ✅ Print Final Data
print(df[["interests", "Cohort"]])


# In[ ]:


##################################################COHORT########################################################################


# In[63]:


from pymongo import MongoClient
import pandas as pd

# ✅ Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["user_database"]  # Replace with your DB name
collection = db["cohort"]  # Replace with your collection name

# ✅ Load Data from MongoDB
cursor = collection.find({}, {"_id": 0, "data": 1})  # Excluding _id
data = list(cursor)
df = pd.DataFrame(data)

# ✅ Extract 'interests' into a new column
df["interests"] = df["data"].apply(lambda x: x.get("interests", []) if isinstance(x, dict) else [])

print(df.head())  # ✅ Check the structure


# In[65]:


# ✅ Define Interest Categories (Lowercase Matching)
interest_categories = {
    "Sports": ["sports", "football", "basketball", "cricket", "tennis"],
    "Tech": ["tech", "ai", "gadgets", "programming", "blockchain"],
    "Movies": ["movies", "hollywood", "bollywood", "action", "drama"],
    "Finance": ["finance", "stock market", "investment", "banking", "crypto"]
}

# ✅ Function to Assign User Cohort
def assign_cohort(interests):
    if isinstance(interests, float) or interests is None:  # Handle NaN or None values
        return "Other"  

    if isinstance(interests, str):  
        interests = interests.lower().split(",")  # Convert string to a list of words

    interests = [i.lower().strip() for i in interests]  # Normalize interests

    for category, keywords in interest_categories.items():
        if any(interest in keywords for interest in interests):
            return category
    return "Other"

# ✅ Apply Cohort Assignment  
df["Cohort"] = df["interests"].apply(assign_cohort)  

print(df[["interests", "Cohort"]])



# In[66]:


import seaborn as sns
import matplotlib.pyplot as plt

# ✅ Count Users per Cohort
cohort_counts = df["Cohort"].value_counts()

# ✅ Plot Cohort Distribution
plt.figure(figsize=(8, 5))
sns.barplot(y=cohort_counts.index, x=cohort_counts.values, palette="viridis")
plt.xlabel("User Count")
plt.ylabel("Cohort")
plt.title("User Cohort Distribution by Interests")
plt.show()


# In[67]:


# ✅ Extract Income Information
df["income"] = df["data"].apply(lambda x: x.get("demographics", {}).get("income", "Unknown"))

# ✅ Group by Income Bracket
income_counts = df["income"].value_counts()

# ✅ Plot Income Distribution
plt.figure(figsize=(10, 6))
sns.barplot(y=income_counts.index, x=income_counts.values, palette="coolwarm")
plt.xlabel("User Count")
plt.ylabel("Income Bracket")
plt.title("User Distribution by Income")
plt.show()


# In[ ]:





# In[ ]:




