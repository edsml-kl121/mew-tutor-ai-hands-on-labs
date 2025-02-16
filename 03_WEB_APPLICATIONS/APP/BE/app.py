from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()  # take environment variables from .env.
gemini_api_key = os.getenv("GEMINI_API_KEY", None)
# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=gemini_api_key)  # Replace with your Gemini API key
# model = genai.GenerativeModel('gemini-pro')

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    # Generate response using Gemini API
    try:
        # chat_session = model.start_chat(
        #     history=[
        #     ]
        # )
        # response = chat_session.send_message(user_message)

        # reply = response.text
        time.sleep(1)
        reply = "hi"
    except Exception as e:
        reply = f"Error generating response: {str(e)}"

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")