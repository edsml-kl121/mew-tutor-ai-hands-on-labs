from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory data to simulate a database
bookings = [
    {"id": 1, "name": "Alice", "roomType": "Single", "nights": 2},
    {"id": 2, "name": "Bob", "roomType": "Double", "nights": 3}
]

# GET all bookings
@app.route("/bookings", methods=["GET"])
def get_bookings():
    return jsonify(bookings)

# POST a new booking
@app.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()
    new_booking = {
        "id": len(bookings) + 1,
        "name": data.get("name"),
        "roomType": data.get("roomType"),
        "nights": data.get("nights", 1)  # default 1 if not provided
    }
    bookings.append(new_booking)
    return jsonify(new_booking), 201

# PATCH (update) a specific booking
@app.route("/bookings/<int:booking_id>", methods=["PATCH"])
def update_booking(booking_id):
    data = request.get_json()
    for booking in bookings:
        if booking["id"] == booking_id:
            # Update only the fields provided
            if "name" in data:
                booking["name"] = data["name"]
            if "roomType" in data:
                booking["roomType"] = data["roomType"]
            if "nights" in data:
                booking["nights"] = data["nights"]
            return jsonify(booking)
    return jsonify({"message": "Booking not found"}), 404

# DELETE a specific booking
@app.route("/bookings/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    for idx, booking in enumerate(bookings):
        if booking["id"] == booking_id:
            deleted_booking = bookings.pop(idx)
            return jsonify(deleted_booking)
    return jsonify({"message": "Booking not found"}), 404

# Run the app
if __name__ == "__main__":
    app.run(debug=True)