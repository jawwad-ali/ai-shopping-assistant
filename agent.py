from connection import model
from agents import Agent, handoff
from tools import product_finder, get_all_products_and_categories, get_discount, billing_agent_handoff

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
    tools = [billing_agent_handoff]
)

second_agent: Agent = Agent(
    name = 'Second Assistant',
    instructions =  """
                        If user ask about product handoff to the agent named agent. 
                        If user ask to generate bill handoff task to the billing agent.
                    """,
    handoffs = [handoff(billing_agent, billing_agent)],
)