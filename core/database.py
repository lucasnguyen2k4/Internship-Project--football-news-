import json
import os
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["football_news"]
collection = db["cleaned_articles"]

def save(json_path):
    with open(json_path, "r", encoding = "utf-8") as f:
        articles = json.load(f)
        if articles:
            collection.insert_many(articles)
            print(f"Inserted {len(articles)} articles from {json_path}")
for filename in os.scandir("data/rss_clean_final"):
    save(filename)