from typing import cast
import chainlit as cl
from agents import Agent, Runner
from agents.run import RunConfig
from connection import config

# Custom module
from agent import agent, billing_agent

@cl.on_chat_start
async def on_chart_start():

    # Setting the session variables on every new session
    cl.user_session.set('chat_history', [])
    cl.user_session.set('config', config)
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
        ### First Agent
        result = await Runner.run(
                    starting_agent = agent,
                    input=history,
                    run_config=config
                )
        
        response_content = result.final_output
        
        # Update the thinking message with the actual response
        msg.content = response_content
        await msg.update()
    
        # Update the session with the new history.
        cl.user_session.set("chat_history", result.to_input_list())

        ###  Second Agent
        
        if 'generate bill' in message.content:
            billing_agent_result = await Runner.run(
                starting_agent = billing_agent,
                input = history + [{
                    "role": "user",
                    "content": "place the order and generate bill for the product I have purchased. Donot generate bill for the entire "
                    "store products. Only generate the bill for one product at a time"
                }],
                run_config = config
            )

            print("Async agent <==>",billing_agent_result.final_output)

            msg.content = billing_agent_result.final_output
            await msg.update()

    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")