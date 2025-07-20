# backend/services/product_service.py
"""Product service for handling product database operations."""

from typing import Dict, Any, List, Tuple

from core.config import settings


class ProductService:
    """Service for handling product operations."""
    
    def __init__(self):
        """Initialize the product service."""
        self.product_db = settings.PRODUCT_DB
    
    def search_products(self, products: List[str]) -> Dict[str, Any]:
        """Search for products in the database."""
        search_results = {}
        
        for product in products:
            product_key = product.lower().strip()
            if product_key in self.product_db:
                search_results[product] = self.product_db[product_key]
            else:
                search_results[product] = {
                    "name": product, 
                    "price": 0, 
                    "in_stock": False
                }
        
        return search_results
    
    def format_search_results(self, search_results: Dict[str, Any]) -> str:
        """Format search results into a user-friendly message."""
        if not search_results:
            return "I couldn't find any products in your query. Could you specify what you'd like to order?"
        
        available_products = []
        unavailable_products = []
        
        for product, result in search_results.items():
            if result.get("in_stock", False):
                available_products.append(f"{result['name']} (${result['price']})")
            else:
                unavailable_products.append(product.title())
        
        if available_products:
            message = f"✅ Available: {', '.join(available_products)}"
            if unavailable_products:
                message += f"\n❌ Not available: {', '.join(unavailable_products)}"
            message += f"\n\nWould you like to order any of these? 😊"
        else:
            message = f"❌ Sorry, none of these products are available: {', '.join(unavailable_products)}"
        
        return message
    
    def get_available_products(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get only available products from search results."""
        return {k: v for k, v in search_results.items() if v.get("in_stock", False)}
    
    def calculate_order_total(self, product: Dict[str, Any], quantity: int) -> float:
        """Calculate total price for an order."""
        return product["price"] * quantity
    
    def format_order_confirmation(self, product: Dict[str, Any], quantity: int) -> str:
        """Format order confirmation message."""
        total = self.calculate_order_total(product, quantity)
        return f"Order confirmed: {quantity} {product['name']}(s) for ${total:.2f}\n\nThank you for your order! 🎉"


# Global product service instance
product_service = ProductService()