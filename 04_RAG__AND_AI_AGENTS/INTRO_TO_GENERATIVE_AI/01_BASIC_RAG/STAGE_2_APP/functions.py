import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from google.genai.types import EmbedContentConfig
from dotenv import load_dotenv

load_dotenv()
# Set up the Gemini client - ensure you have your API key set in environment variables

api_key = os.environ.get("GEMINI_API_KEY")
print(api_key)
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable")

client = genai.Client(api_key=api_key)


# Mock restaurant data for Bangkok
restaurants = [
    {
        "name": "La Dotta",
        "description": "Authentic Italian restaurant specializing in handmade pasta dishes using imported ingredients from Italy. Located in Thonglor district of Bangkok.",
        "price_range": "$$",
        "address": "161/6 Thonglor Soi 9, Bangkok 10110",
        "cuisine": "Italian",
        "popular_dishes": ["Truffle Tagliatelle", "Cacio e Pepe", "Seafood Linguine"]
    },
    {
        "name": "Peppina",
        "description": "Neapolitan pizza restaurant with wood-fired ovens imported from Italy. Features traditional Italian dishes and a wide selection of Italian wines.",
        "price_range": "$$",
        "address": "27/1 Sukhumvit Soi 33, Bangkok 10110",
        "cuisine": "Italian, Pizza",
        "popular_dishes": ["Margherita Pizza", "Burrata", "Tiramisu"]
    },
    {
        "name": "L'Oliva",
        "description": "High-end Italian dining with focus on Northern Italian cuisine. Offers homemade pasta, risotto, and seafood specialties in the heart of Sukhumvit.",
        "price_range": "$$$",
        "address": "4 Sukhumvit Soi 36, Bangkok 10110",
        "cuisine": "Italian, Fine Dining",
        "popular_dishes": ["Risotto ai Funghi", "Osso Buco", "Branzino"]
    },
    {
        "name": "Appia",
        "description": "Roman-inspired trattoria serving hearty Italian comfort food including porchetta and homemade pasta in a rustic setting in Sukhumvit Soi 31.",
        "price_range": "$$$",
        "address": "20/4 Sukhumvit Soi 31, Bangkok 10110",
        "cuisine": "Italian, Roman",
        "popular_dishes": ["Porchetta", "Carbonara", "Saltimbocca"]
    },
    {
        "name": "Pizza Massilia",
        "description": "Upscale Italian restaurant specializing in gourmet pizzas with premium imported ingredients and authentic Italian recipes with a modern twist.",
        "price_range": "$$$",
        "address": "Sukhumvit Soi 49, Bangkok 10110",
        "cuisine": "Italian, Pizza",
        "popular_dishes": ["Truffle Pizza", "Parma Pizza", "Seafood Pizza"]
    },
    {
        "name": "Gianni's",
        "description": "Classic Italian restaurant in Sukhumvit offering traditional dishes from various regions of Italy, with an extensive wine collection.",
        "price_range": "$$$",
        "address": "34/1 Sukhumvit Soi 23, Bangkok 10110",
        "cuisine": "Italian",
        "popular_dishes": ["Lasagna", "Veal Milanese", "Panna Cotta"]
    },
    {
        "name": "Som Tam Nua",
        "description": "Popular Thai restaurant specializing in Northeastern Thai cuisine, especially spicy papaya salad and grilled chicken. Located in Siam Square.",
        "price_range": "$",
        "address": "392/14 Siam Square Soi 5, Bangkok 10330",
        "cuisine": "Thai, Isaan",
        "popular_dishes": ["Som Tam", "Gai Yang", "Larb Moo"]
    },
    {
        "name": "Pad Thai Ekkamai",
        "description": "Local favorite serving authentic pad thai and other traditional Thai noodle dishes in the trendy Ekkamai neighborhood.",
        "price_range": "$",
        "address": "337/5 Ekkamai Soi 2, Bangkok 10110",
        "cuisine": "Thai",
        "popular_dishes": ["Pad Thai", "Pad See Ew", "Guay Teow"]
    },
    {
        "name": "Isaan Der",
        "description": "Northeastern Thai cuisine featuring grilled meats, sticky rice, and spicy salads served in a casual atmosphere near Asok.",
        "price_range": "$",
        "address": "5/8 Sukhumvit Soi 20, Bangkok 10110",
        "cuisine": "Thai, Isaan",
        "popular_dishes": ["Nam Tok Moo", "Som Tam", "Moo Ping"]
    },
    {
        "name": "Gaggan",
        "description": "Progressive Indian restaurant offering innovative tasting menus with modern techniques while maintaining authentic flavors. Located in Lumpini.",
        "price_range": "$$$$",
        "address": "68/1 Soi Langsuan, Ploenchit Road, Bangkok 10330",
        "cuisine": "Indian, Molecular Gastronomy",
        "popular_dishes": ["Yogurt Explosion", "Charcoal", "Pork Vindaloo"]
    },
]

def get_embedding(text):
    """Get text embedding from Gemini API"""
    embed_model = "text-embedding-004"
    response = client.models.embed_content(
        model=embed_model,
        contents=[text],
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY" if len(text) < 100 else "RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
        ),
    )
    return np.array(response.embeddings[0].values)

def create_restaurant_embeddings():
    """Create and return restaurant embeddings - this is the time-consuming step"""
    print("Generating restaurant embeddings... (this may take a while the first time)")
    
    # Prepare document embeddings and content
    restaurant_texts = [f"{r['name']}: {r['description']}" for r in restaurants]
    
    # Generate all embeddings
    restaurant_embeddings = []
    for i, text in enumerate(restaurant_texts):
        print(f"  Embedding restaurant {i+1}/{len(restaurant_texts)}: {restaurants[i]['name']}")
        embedding = get_embedding(text)
        restaurant_embeddings.append(embedding)
    
    print("Embedding generation complete!\n")
    return restaurant_embeddings

def search_restaurants(query, restaurant_embeddings, top_k=5):
    """Search restaurants based on query and pre-generated embeddings"""
    print(f"Generating query embedding for: '{query}'")
    
    # Get query embedding
    query_embedding = get_embedding(query)
    
    print("Calculating similarities...")
    
    # Calculate similarities
    similarities = []
    for i, doc_embedding in enumerate(restaurant_embeddings):
        similarity = cosine_similarity([query_embedding], [doc_embedding])[0][0]
        similarities.append({
            "restaurant": restaurants[i],
            "similarity": similarity
        })
    
    # Sort by similarity (highest first)
    sorted_results = sorted(similarities, key=lambda x: x["similarity"], reverse=True)
    
    # Return top k results
    return sorted_results[:top_k]

def generate_response(query, context):
    """Generate a response using Gemini based on the query and retrieved context"""
    # model = genai.GenerativeModel(generation_model)
    
    prompt = f"""
You are a helpful restaurant recommendation assistant for Bangkok.
Use the provided restaurant information to answer the user's query.
Only recommend restaurants from the information provided.
If the query asks for something not in the provided information, politely indicate 
that you don't have that specific information but suggest the closest alternatives.

USER QUERY: {query}

RESTAURANT INFORMATION:
{context}

Please provide a helpful response that directly answers the user's query based on the restaurant information above.
Include specific details about the restaurants where relevant, such as popular dishes, location, and price range.
"""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    )
    
    return response.text

