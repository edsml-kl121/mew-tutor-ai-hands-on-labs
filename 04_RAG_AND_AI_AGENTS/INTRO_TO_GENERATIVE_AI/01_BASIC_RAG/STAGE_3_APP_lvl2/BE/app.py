from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
# import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
from function import get_milvus_client, search_embedding, generate
from pymilvus import Collection
from schema.text_vector import collection_name, schema

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY", None)

# Initialize FastAPI app
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

get_milvus_client()

collection = Collection(name=collection_name, schema=schema)
collection.load()

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
      user_message = request.message
      results = search_embedding(collection, user_message)
      docs = ""
      for result in results[0]:
          # print("Matched text:", result.entity.get("chunk_content"), "score:", result.distance)
          docs += "--------------------------\n"
          docs += result.entity.get("chunk_content")
        # print(result.entity.get("chunk_content"))
      reply = generate(user_message, docs)
    except Exception as e:
        reply = f"Error generating response: {str(e)}"

    return JSONResponse(content={"reply": reply})