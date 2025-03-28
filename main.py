from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

from tools import product_finder, get_all_products_and_categories, get_discount
from connection import gemini_api_key

@cl.on_chat_start
async def on_chart_start():
    external_client = AsyncOpenAI(
        api_key = gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    model = OpenAIChatCompletionsModel(
        model = "gemini-2.0-flash",
        openai_client = external_client
    )
    config = RunConfig(
        model = model,
        model_provider = external_client,
        tracing_disabled = True
    )

    cl.user_session.set('chat_history', [])
    cl.user_session.set('config', config)

    agent: Agent = Agent(
        name = 'Assistant', 
        instructions = 'You are a helpful shopping assistant/agent. You can provide information about products like their name, price, color,size etc'
                        ' answer questions', 
        model = model,
        tools=[product_finder, get_all_products_and_categories, get_discount]
        )
    cl.user_session.set('agent', agent)

    await cl.Message(content="Welcome to the Ali Shopping Store! How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content = 'Thinking...')
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get('agent'))
    config: RunConfig = cast(RunConfig, cl.user_session.get('config'))

    history = cl.user_session.get('chat_history') or []
    history.append({'role': 'user' , 'content': message.content})

    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        result = Runner.run_sync(starting_agent = agent,
                    input=history,
                    run_config=config)
        
        response_content = result.final_output
        
        # Update the thinking message with the actual response
        msg.content = response_content
        await msg.update()
    
        # Update the session with the new history.
        cl.user_session.set("chat_history", result.to_input_list())
        
        # Optional: Log the interaction
        # print(f"User: {message.content}")
        # print(f"Assistant: {response_content}")
        
    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")
