from pymilvus import FieldSchema, CollectionSchema, DataType

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="chunk_content", dtype=DataType.VARCHAR, max_length=5192),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
]

schema = CollectionSchema(fields, description="Text + vector collection")
collection_name = "mew_collection"