# Test the homepage (GET /)
curl -X GET http://localhost:5000/

# Get all items (GET /items)
curl -X GET http://localhost:5000/items

# Create a new item (POST /items)
curl -X POST \
  http://localhost:5000/items \
  -H 'Content-Type: application/json' \
  -d '{"name": "New Item", "description": "Description for the new item"}'

# Update an item (PUT /items/<id>) - Replace <id> with an actual item ID
curl -X PUT \
  http://localhost:5000/items/1 \
  -H 'Content-Type: application/json' \
  -d '{"name": "Updated Item", "description": "Updated description"}'

# Partially update an item (PATCH /items/<id>) - Replace <id> with an actual item ID
curl -X PATCH \
  http://localhost:5000/items/1 \
  -H 'Content-Type: application/json' \
  -d '{"description": "Only update the description"}'

# Delete an item (DELETE /items/<id>) - Replace <id> with an actual item ID
curl -X DELETE http://localhost:5000/items/1