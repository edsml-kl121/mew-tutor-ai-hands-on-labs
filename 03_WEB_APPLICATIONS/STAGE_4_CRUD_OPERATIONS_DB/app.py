from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from database import get_db_connection, init_db

app = FastAPI()

# Initialize the database before the first request
init_db()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Home route
@app.get("/", response_class=HTMLResponse)
async def hello_world(request: Request):
    """Route for the homepage, returns HTML hello world"""
    return templates.TemplateResponse("home.html", {"request": request})

# GET all items
@app.get("/items")
async def get_items():
    """Route to GET all data from SQLite"""
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    
    # Convert the items to a list of dictionaries
    result = [dict(item) for item in items]
    return JSONResponse(content=result)

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """Route to GET a specific item by ID"""
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
    
    return JSONResponse(content=dict(item))

class ItemRequest(BaseModel):
    name: str
    description: Optional[str] = ""

# POST (create) an item
@app.post("/items", status_code=201)
async def add_item(request: Request):
    """Route to POST (add) data to SQLite"""
    if request.headers.get("content-type") != "application/json":
        raise HTTPException(status_code=400, detail="Request must be JSON")
    
    data = await request.json()
    
    # Validate the required fields
    if 'name' not in data:
        raise HTTPException(status_code=400, detail="Name field is required")
    
    name = data['name'] # Will raise error if key doesn't exist. (Required field)
    description = data.get('description', '') # No error raised if key doesn't exist. (Optional field)

    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO items (name, description) VALUES (?, ?)',
        (name, description)
    )
    conn.commit()
    
    # Get the ID of the newly inserted item
    item_id = cursor.lastrowid
    conn.close()
    
    return JSONResponse(content={
        "id": item_id,
        "name": name,
        "description": description,
        "message": "Item created successfully"
    })

# PUT (update) an item
@app.put("/items/{item_id}")
async def update_item(item_id: int, request: Request):
    """Route to PUT (update) data in SQLite"""
    if request.headers.get("content-type") != "application/json":
        raise HTTPException(status_code=400, detail="Request must be JSON")
    
    data = await request.json()
    
    # Get current item to check if it exists
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    
    if item is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
    
    # Update the item with new values or keep existing ones
    name = data.get('name', item['name'])
    description = data.get('description', item['description'])
    
    conn.execute(
        'UPDATE items SET name = ?, description = ? WHERE id = ?',
        (name, description, item_id)
    )
    conn.commit()
    conn.close()
    
    return JSONResponse(content={
        "id": item_id,
        "name": name,
        "description": description,
        "message": "Item updated successfully"
    })

# DELETE an item
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Route to DELETE data from SQLite"""
    conn = get_db_connection()
    
    # Check if the item exists
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    
    if item is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
    
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    return JSONResponse(content={
        "message": f"Item with id {item_id} deleted successfully"
    })

# To run:
# uvicorn your_filename:app --reload --port 5000