from pymilvus import Collection
from function import get_milvus_client

get_milvus_client()
# Replace with your collection name
collection = Collection("mew_collection")
collection.drop()