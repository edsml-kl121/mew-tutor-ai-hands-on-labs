1. `pip install -r requirement.txt`

2. Choose one command. (All will work)
`python app.py` or `uvicorn app:app --reload --port 5000` for development
`uvicorn app:app --host 0.0.0.0 --port 5000` for production

3. 
```
curl -X POST http://localhost:5000/append_hello \
  -H "Content-Type: application/json" \
  -d '{"text": "World "}'
```

