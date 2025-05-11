from pymilvus import utility, Collection
from function import get_embedding, get_milvus_client, get_data
from schema.text_vector import schema, collection_name
get_milvus_client()
data_dictionary = get_data('../EXTRACTION/thai_leave_policy_chunks.csv')

print("✅ Connected to Zilliz Cloud Milvus.")

collection = Collection(name=collection_name, schema=schema)
collections = utility.list_collections()

print("Collections:", collections)
texts = ["hello world", "zilliz cloud vector", "chatgpt rocks"]
vectors = []
for text in data_dictionary["chunk_content"]:
    vectors.append(get_embedding(text))

data = [data_dictionary["title"], data_dictionary["chunk_content"], vectors]
# data
collection.insert(data)
# collection.flush()

collection.create_index(
    field_name="embedding",
    index_params={
        "metric_type": "L2",         # or "COSINE", "IP"
        "index_type": "IVF_FLAT",    # or "HNSW", "IVF_PQ", etc.
        "params": {"nlist": 128}
    }
)



### Metrics

## Lower value -> more similar
# Eulidean Distance (L2) - Straightline distance between two vectors
# Small distance -> Similar. [0, inf)

## higher value -> more similar
# Cosine Similarity - Cosine of the angle between two vectors. Focusing on their orientation rather than magnitude.
# similar -> 1.0 [-1,1]
# Inner Product - Calculates the sum of the products of corresponding vectors components.
# higher value -> more similar (-inf, inf)

### Index Types
# Flat - Brute force search. Fastest for small datasets.
# IVF_FLAT - Partitions the dataset into clusters using k-means clustering. During a search,
# only subset is examined increasing speed.
# HNSW (Hierarchical Navigable Small world) - Employs a graph-based approach to create a navigable small world network. 
