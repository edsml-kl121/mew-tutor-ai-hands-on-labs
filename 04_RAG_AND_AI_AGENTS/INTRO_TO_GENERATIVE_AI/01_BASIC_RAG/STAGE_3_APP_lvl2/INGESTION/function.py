import os
from dotenv import load_dotenv
from pymilvus import connections
from google import genai
from google.genai.types import EmbedContentConfig
import numpy as np
import pandas as pd

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
url = os.environ.get("ZILLIZ_URL")
token = os.environ.get("ZILLIZ_TOKEN")

client = genai.Client(api_key=api_key)
embed_model = "text-embedding-004"

def get_milvus_client():
    connections.connect(
        alias="default",
        uri=url,  # Full HTTPS URI
        token=token  # Format: user:password
    )


def get_embedding(text):
    """Get text embedding from Gemini API"""
    response = client.models.embed_content(
        model=embed_model,
        contents=[text],
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY" if len(text) < 100 else "RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
        ),
    )
    return np.array(response.embeddings[0].values)

def search_embedding(collection, current_search_term):
    search_embedding = get_embedding(current_search_term)

    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        [search_embedding],
        # search_embedding,
        "embedding",
        search_params,
        limit=3,
        output_fields=["chunk_content"]
    )
    return results

def get_data(file_path='assets/extracted_data'):
    df = pd.read_csv(file_path)
    df = df.astype(str)

    # Get the column names from the DataFrame
    column_names = df.columns

    # Initialize an empty dictionary to store lists for each column
    data_dict = {}

    # Loop through each column and translate its values
    for column in column_names:
        values = df[column].tolist()
        data_dict[column] = values
    return data_dict