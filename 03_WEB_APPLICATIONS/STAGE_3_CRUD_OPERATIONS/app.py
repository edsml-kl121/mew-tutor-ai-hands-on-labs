from flask import Flask, request, jsonify, render_template
from database import get_db_connection, init_db

app = Flask(__name__)

# Initialize the database before the first request
init_db()

# Home route
@app.route('/')
def hello_world():
    """Route for the homepage, returns HTML hello world"""
    return render_template('home.html')

# GET all items
@app.route('/items', methods=['GET'])
def get_items():
    """Route to GET all data from SQLite"""
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    
    # Convert the items to a list of dictionaries
    result = [dict(item) for item in items]
    return jsonify(result)

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Route to GET a specific item by ID"""
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    
    if item is None:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    
    return jsonify(dict(item))

# POST (create) an item
@app.route('/items', methods=['POST'])
def add_item():
    """Route to POST (add) data to SQLite"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Validate the required fields
    if 'name' not in data:
        return jsonify({"error": "Name field is required"}), 400
    
    name = data['name'] # Will raise error if key doesn't exist. (Required field)
    description = data.get('description', '') # No error raised if key doesn't exist. (Optional field)3
    
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO items (name, description) VALUES (?, ?)',
        (name, description)
    )
    conn.commit()
    
    # Get the ID of the newly inserted item
    item_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        "id": item_id,
        "name": name,
        "description": description,
        "message": "Item created successfully"
    }), 201

# PUT (update) an item
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Route to PUT (update) data in SQLite"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Get current item to check if it exists
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    
    if item is None:
        conn.close()
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    
    # Update the item with new values or keep existing ones
    name = data.get('name', item['name'])
    description = data.get('description', item['description'])
    
    conn.execute(
        'UPDATE items SET name = ?, description = ? WHERE id = ?',
        (name, description, item_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        "id": item_id,
        "name": name,
        "description": description,
        "message": "Item updated successfully"
    })

# DELETE an item
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Route to DELETE data from SQLite"""
    conn = get_db_connection()
    
    # Check if the item exists
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    
    if item is None:
        conn.close()
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": f"Item with id {item_id} deleted successfully"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # http://127.0.0.1:5000/
