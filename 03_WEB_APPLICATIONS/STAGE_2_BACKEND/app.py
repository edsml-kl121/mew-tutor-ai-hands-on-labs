from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
import uvicorn

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/append_hello", response_class=PlainTextResponse)
async def append_hello(input: TextInput):
    return input.text + "Hello"

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)