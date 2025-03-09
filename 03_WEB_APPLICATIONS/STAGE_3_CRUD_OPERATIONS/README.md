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

# Create an item and capture its ID for further operations
ITEM_ID=$(curl -s -X POST \
  http://localhost:5000/items \
  -H 'Content-Type: application/json' \
  -d '{"name": "Test Item", "description": "Item for testing"}' \
  | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

echo "Created item with ID: $ITEM_ID"

# Use the captured ID
curl -X PUT \
  http://localhost:5000/items/$ITEM_ID \
  -H 'Content-Type: application/json' \
  -d '{"description": "Updated test description"}'

# Delete the item we just created
curl -X DELETE http://localhost:5000/items/$ITEM_ID

# Test error cases

# Test invalid JSON format
curl -X POST \
  http://localhost:5000/items \
  -H 'Content-Type: application/json' \
  -d '{"invalid_json":}'

# Test missing required field
curl -X POST \
  http://localhost:5000/items \
  -H 'Content-Type: application/json' \
  -d '{"description": "Missing name field"}'

# Test updating non-existent item
curl -X PUT \
  http://localhost:5000/items/9999 \
  -H 'Content-Type: application/json' \
  -d '{"name": "Non-existent Item"}'

# Test deleting non-existent item
curl -X DELETE http://localhost:5000/items/9999