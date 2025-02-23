import requests

# Define the API endpoint
url = "http://127.0.0.1:5000/append_hello"  # Ensure Flask is running locally

# Data to send in the request
data = {"text": "Hi, "}

# Send a POST request
response = requests.post(url, data=data)

# Print the response from the server
print("Response:", response.text)