from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["football_news"]
mongo_collection = mongo_db["cleaned_articles"]

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "AjHJ8y3ZPnroSXIvKK_f"),  
    verify_certs=False
)

index_name = "football_news"

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f" Deleted existing index: {index_name}")

es.indices.create(index=index_name, body={
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "summary": {"type": "text"},
            "url": {"type": "keyword"},
            "date": {"type": "date"},
            "source": {"type": "keyword"},
            "clubs": {"type": "keyword"},  
            "leagues": {"type": "keyword"},
            "main_league": {"type": "keyword"}  
        }
    }
})
print(f" Created index: {index_name}")

def generate_documents():
    for doc in mongo_collection.find():
        doc.pop("_id", None) 
        yield {
            "_index": index_name,
            "_source": doc
        }

success, _ = bulk(es, generate_documents())
print(f"Successfully indexed {success} documents into {index_name}")
