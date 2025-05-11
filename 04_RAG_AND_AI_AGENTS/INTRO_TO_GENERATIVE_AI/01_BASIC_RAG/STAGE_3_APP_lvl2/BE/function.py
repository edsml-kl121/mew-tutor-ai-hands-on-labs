import os
from dotenv import load_dotenv
from pymilvus import connections
from google import genai
from google.genai.types import EmbedContentConfig
import numpy as np
from google import genai
from google.genai import types

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
        limit=5,
        output_fields=["chunk_content"]
    )
    return results


def generate(user_query, results):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    user_message = f"""Please answer the user's query: {user_query} based on this documentation: {results}"""
    print(user_message)
    model="gemini-2.0-flash-exp"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""hi"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""Hi there! How can I help you today?
"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_message),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        temperature=1,
    )
    final_chunk = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        final_chunk += chunk.text
        print(chunk.text, end="")
    return final_chunk