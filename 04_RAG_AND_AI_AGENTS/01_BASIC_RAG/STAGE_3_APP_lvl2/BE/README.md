## Command to start app.
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
app:app = filename:FastAPI_instance

## Exposing endpoint to public
Side Note: ngrok http 8000

## Test endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Gemini!"}'