from pydantic import BaseModel, Field
from langchain.tools import Tool
from function import semantic_search
from langchain.tools import StructuredTool
import random
from typing import List

class GroceryInvetorySearchTool:
    # def __init__(self):
    #     self.message_history = 
    #     self.llm = 
    def handle_query(self, user_input):
        index_name = "grocery-index"
        output = semantic_search(index_name, user_input, 20)
        return output

    def get_tool(self):
        return Tool.from_function(
            func=self.handle_query,
            name="GroceryInvetorySearchTool",
            description="Use this tool to search individual ingredients or products that exists in the retail store."
        )

class RecommenderInput(BaseModel):
    customer_id: int = Field(..., description="The ID of the customer")
    num_recommendations: int = Field(default=3, description="Number of products to recommend", ge=1, le=10)

class RecommenderSystemTool:
    def __init__(self):
        # Mock product data: product_id mapped to product_name
        self.products = {
            1: "Apples",
            2: "Bananas",
            3: "Carrots",
            4: "Dairy Milk",
            5: "Eggs",
            6: "Fish",
            7: "Grapes",
            8: "Honey",
            9: "Iceberg Lettuce",
            10: "Juice"
        }

    def recommend_products(self, 
                         customer_id: int,
                         num_recommendations: int = 3) -> List[str]:
        """
        Recommend a list of products to a customer.

        Args:
            customer_id: The ID of the customer
            num_recommendations: Number of products to recommend (default: 3)

        Returns:
            A list of recommended product names

        Raises:
            ValueError: If num_recommendations is greater than the number of available products
        """
        if num_recommendations > len(self.products):
            raise ValueError(f"Cannot recommend more products than available. Maximum is {len(self.products)}")

        # For demonstration, randomly select products to recommend
        recommended_ids = random.sample(list(self.products.keys()), num_recommendations)
        recommendations = [self.products[pid] for pid in recommended_ids]
        return recommendations

    def get_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.recommend_products,
            name="RecommenderSystemTool",
            description="Use this tool to recommend products to customers based on their preferences",
            args_schema=RecommenderInput
        )
#         )



class OrderInput(BaseModel):
    customer_id: str = Field(..., description="The ID of the customer")
    name: str = Field(..., description="The name of the customer must be filled")
    address: str = Field(..., description="The address of the customer must be filled by the user")
    product_id: str = Field(..., description="The ID of the product")
    product_quantity: str = Field(..., description="The quantity of the product")

class OrderProcessorTool:
    def place_order(self, 
                    customer_id: str,
                    name: str,
                    address: str,
                    product_id: str,
                    product_quantity: str) -> str:
        """
        Place an order for a customer and return a confirmation message. Ensure you get all the arguements before using the tool

        Args:
            customer_id: The ID of the customer
            name: The name of the customer
            address: The address of the customer
            product_id: The ID of the product
            product_quantity: The quantity of the product

        Returns:
            A confirmation message with the order details
        """
        # Simulate order processing logic
        confirmation_message = (
            f"Order placed successfully!\n"
            f"Customer ID: {customer_id}\n"
            f"Name: {name}\n"
            f"Address: {address}\n"
            f"Product ID: {product_id}\n"
            f"Product Quantity: {product_quantity}"
        )
        print(confirmation_message)
        return confirmation_message

    def get_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self.place_order,
            name="OrderProcessorTool",
            description="Use this tool to place orders for customers, but ensure you have all required inputs first. ask users for more information. ",
            args_schema=OrderInput
        )