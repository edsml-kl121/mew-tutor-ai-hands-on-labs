Here is the content in Markdown format:

# Flask App API Documentation

## Running the Flask App

To start the Flask app, run the following command:

```bash
python app.py

The server will start on http://127.0.0.1:5000 by default.

Example curl Commands

Replace localhost:5000 with your own server/port if it differs.

1. GET - Retrieve All Bookings

Retrieve a list of all current bookings:

curl -X GET http://localhost:5000/bookings

Sample Response (HTTP 200):

[
  { "id": 1, "name": "Alice", "roomType": "Single", "nights": 2 },
  { "id": 2, "name": "Bob", "roomType": "Double", "nights": 3 }
]

2. POST - Create a New Booking

Create a new booking by sending the details in JSON format:

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Charlie",
    "roomType": "Suite",
    "nights": 5
  }' \
  http://localhost:5000/bookings

Sample Response (HTTP 201):

{
  "id": 3,
  "name": "Charlie",
  "roomType": "Suite",
  "nights": 5
}

3. PATCH - Update a Booking

Update the roomType of the booking with id=3 to “Single”:

curl -X PATCH \
  -H "Content-Type: application/json" \
  -d '{
    "roomType": "Single"
  }' \
  http://localhost:5000/bookings/3

Sample Response (HTTP 200):

{
  "id": 3,
  "name": "Charlie",
  "roomType": "Single",
  "nights": 5
}

4. DELETE - Remove a Booking

Delete the booking with id=3:

curl -X DELETE http://localhost:5000/bookings/3

Sample Response (HTTP 200):

{
  "id": 3,
  "name": "Charlie",
  "roomType": "Single",
  "nights": 5
}

Summary of Endpoints
	•	GET /bookings: Retrieves a list of all current bookings.
	•	POST /bookings: Creates a new booking (requires JSON body).
	•	PATCH /bookings/<id>: Partially updates existing bookings.
	•	DELETE /bookings/<id>: Removes a specific booking from the list.

