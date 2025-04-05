from connection import config, model, external_client
from agents import Agent, Runner, handoff
from tools import product_finder, get_all_products_and_categories, get_discount

# second
def billing_agent_handoff(products):
    """
    Creates or overwrites a bill.txt file with product billing details, including discounts if provided.

    :param products: List of tuples or dictionaries (product_name, product_price, discount_percentage)
                     If no discount, use 0 as the discount_percentage.
    """
    try:
        total = 0
        with open("bill.txt", "w") as file:
            file.write("Product Details:\n")
            file.write("product name\toriginal price\tdiscount\tdiscounted price\n")
            
            for name, price, discount in products:
                discounted_price = price * (1 - discount / 100) if discount > 0 else price
                total += discounted_price
                file.write(f"{name}\t${price:.2f}\t{discount}%\t${discounted_price:.2f}\n")
            
            file.write(f"\nTotal\t\t\t${total:.2f}\n")
        print("Bill generated successfully at 'bill.txt'.")
    except Exception as e:
        print(f"Error generating bill: {str(e)}")

# Initialize the agent with the model and tools
agent: Agent = Agent(   
    name = 'Shopping Assistant', 
    instructions = 'You are a helpful shopping assistant/agent. You can provide information about products like their name, price, color,size etc'
                    ' answer questions', 
    model = model,
    tools=[product_finder, get_all_products_and_categories, get_discount]
)

billing_agent: Agent = Agent(
    name = 'Billing Agent',
    instructions = """
        You are a billing assistant. Begin your task only when the user's query includes the phrase 'generate bill'.

        Your job is to:
        - Generate a bill in a text file named 'bill.txt'.
        - Include each product's name, price, discount and total on a new line.
        - At the end, include the total amount due.

        Assume product information will either be provided by the user or fetched from context. Do not take action unless 'generate bill' is explicitly mentioned.
        """,
    handoff_description="An assistant that generates itemized bills in a text file upon request."
)

second_agent: Agent = Agent(
    name = 'Second Assistant',
    instructions = 'If users ask to generate the bill handoff task to the billing agent',
    handoffs = [handoff(billing_agent , input_filter = billing_agent_handoff  )]
)





# def billing_agent_handoff(products):
#     """
#     Creates or overwrites a bill.txt file with product billing details.

#     :param products: List of tuples or dictionaries (product_name, product_price, discount_percentage)
#                      If no discount, use 0 as the discount_percentage.
#     """
#     try:
#         total = 0
#         with open("bill.txt", "w") as file:
#             file.write("Product Details:\n")
#             file.write("product name\toriginal price\tdiscount\tdiscounted price\n")
            
#             for item in products:
#                 # Handle both tuple and dict formats
#                 if isinstance(item, tuple):
#                     name, price, discount = item
#                 elif isinstance(item, dict):
#                     name = item.get("name", "Unknown")
#                     price = item.get("price", 0)
#                     discount = item.get("discount", 0)
#                 else:
#                     raise ValueError("Invalid product format")
                
#                 discounted_price = price * (1 - discount / 100) if discount > 0 else price
#                 total += discounted_price
#                 file.write(f"{name}\t${price:.2f}\t{discount}%\t${discounted_price:.2f}\n")
            
#             file.write(f"\nTotal\t\t\t${total:.2f}\n")
#         return "Bill generated successfully at 'bill.txt'."
#     except Exception as e:
#         return f"Error generating bill: {str(e)}"