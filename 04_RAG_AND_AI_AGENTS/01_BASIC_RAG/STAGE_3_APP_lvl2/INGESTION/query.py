from function import get_milvus_client, search_embedding
from pymilvus import Collection
from schema.text_vector import collection_name, schema

get_milvus_client()
collection = Collection(name=collection_name, schema=schema)
collection.load()
current_search_term = "Hello world"

results = search_embedding(collection, current_search_term)

for result in results[0]:
    print("Matched text:", result.entity.get("chunk_content"), "score:", result.distance)

