from agents.tool import function_tool
import requests
from model import Product

url = "https://template1-neon-nu.vercel.app/api/products"

@function_tool("product_finder")
def product_finder(product_query: str) -> str:
    """
    Find product details from the API based on the user's query (e.g., product name or ID).
    Returns all available product details for the LLM to process.
    
    Args:
        product_query (str): The product name or ID to search for.
    
    Returns:
        str: Full product details if found, otherwise an error message.
    """
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        products = response.json()
        
        for product in products:
            if (product_query.lower() in product.get("name", "").lower() or 
                product_query == str(product.get("id", ""))):
                # Return all relevant details as a formatted string
                colors = ", ".join(product.get("colors", []))
                sizes = ", ".join(product.get("sizes", []))
                return (
                    f"Product: {product.get('name')}\n"
                    f"Price: ${product.get('price', 'N/A')}\n"
                    f"Colors: {colors}\n"
                    f"Sizes: {sizes}\n"
                    f"Description: {product.get('description', 'N/A')}\n"
                    f"Category: {product.get('category', 'N/A')}"
                )
        
        return "Product not found."
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from API: {str(e)}"
    
@function_tool('get_all_products_and_categories')
def get_all_products_and_categories() -> str:
    """
    Fetch all products from the API and return a list of product names and categories.
    
    Returns:
        str: A formatted string containing all product names and categories.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        products = response.json()
        
        product_list = []
        for product in products:
            product_list.append(f"{product.get('name')} ({product.get('category')})")
        
        return "\n".join(product_list)
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from API: {str(e)}"
    
@function_tool('get_discount')
def get_discount(product_name: str) -> str:
    """
    Fetch the discount for a specific product from the API.
    
    Args:
        product_name (str): The name of the product to search for.
    
    Returns:
        str: The discount percentage if found, otherwise an error message.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        products = response.json()
        
        for product in products:
            if product_name.lower() in product.get("name", "").lower():
                discount = product.get("discountPercent", 0)
                if discount > 0:
                    return f"Discount: {discount}%"
                return "No discount available for this product."
        
        return "Product not found."
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from API: {str(e)}"
    
@function_tool('billing_agent_handoff')
def billing_agent_handoff(products: list[Product]):
    """
    Creates or overwrites a bill.txt file with product billing details, including discounts if provided.

    :param products: List of Product class or dictionaries (name, price, discount, description)
                     If no discount, use 0 as the discount.
    """
    try:
        total = 0
        with open("bill.txt", "a") as file:
            # Write the header once, formatted for the output
            file.write("Product Name: Price: Discount: Discounted Price: Description:\n")
            
            # `Product` is a class with attributes like `name`, `price`, `discount`, and `description`
            for product in products:
                # Access the attributes of the `Product` Tuple
                name = product.name
                price = product.price
                discount = product.discount
                description = product.description
    
                # Calculate discounted price
                discounted_price = price * (1 - discount / 100) if discount > 0 else price
                total += discounted_price
    
                # Write product details in the desired format
                file.write(f"{name}: {price} : {discount}% : {discounted_price:.2f} : {description}\n")
            
            # Write the total at the end
            file.write(f"\nTotal: {total:.2f}\n\n")
        
        print("Bill generated successfully at 'bill.txt'.")
    
    except Exception as e:
        print(f"Error generating bill: {str(e)}")