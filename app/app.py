from plugins.FlightsPlugin import FlightsPlugin
from semantic_kernel.core_skills import TimeSkill
from semantic_kernel.connectors.ai.open_ai import AzureTextCompletion
from planning.autogen_planner import AutoGenPlanner
import semantic_kernel as sk
import logging
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request
import autogen
import asyncio


# Create Flask app
app = Flask(__name__)

# Setup start message
start_msg = {
        'content': 'Hi, I\'m your airline booking agent. Actually, I am multiple agents, but nevermind that. How can we... How can I help you?',
        'role': 'assistant'
}
g_messages = [start_msg]


# Execute user's instructions and populate g_messages with the agents' replies
async def execute_task(instructions: str):

    # Clear global messages list
    reset_messages()

    # Determine script location irrespective of current working directory
    app_dir = os.path.dirname(os.path.realpath(__file__))

    # Load environment variables from `.env` file
    env_path = os.path.join(app_dir, '.env')
    load_dotenv(env_path)

    # Instantiate kernel
    kernel = sk.Kernel()

    # Prepare Azure OpenAI service using credentials stored in the `.env` file
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    kernel.add_text_completion_service('gpt-4', AzureTextCompletion(deployment_name=deployment, endpoint=endpoint, api_key=api_key, api_version='2023-07-01-preview'))

    logging.info('Kernel loaded.')

    # Register plugins
    cosmos_conn_str = os.getenv('COSMOS_CONNECTION_STRING')
    flights_plugin = kernel.import_skill(FlightsPlugin(cosmos_conn_str), skill_name='FlightsPlugin')
    time_skill = kernel.import_skill(TimeSkill(), skill_name='TimeSkill')

    logging.info('Plugins registered.')

    llm_config = {
        'api_type': 'azure',
        'model': deployment,
        'api_key': api_key,
        'base_url': endpoint,
        'api_version': '2023-07-01-preview'
    }

    planner = AutoGenPlanner(kernel, llm_config=llm_config)

    booking_agent = planner.create_assistant_agent('BookingAgent', persona='You are an airline booking agent. You can search for flights and book them. The user cannot reply to any of your messages.')
    worker = planner.create_user_agent('Worker', max_auto_reply=4, human_input='NEVER')

    logging.info('Planner ready.')

    # Register reply functions
    register_reply(booking_agent)
    register_reply(worker)
    logging.info('Reply functions registered.')

    # Start chat

    worker.initiate_chat(booking_agent, message=instructions)

    # The last message always has role 'user', which may be a bug
    # Change it to role 'assistant' to be displayed correctly
    g_messages[-1]['role'] = 'assistant'


# Register reply function, so that when a message is sent to the agent,
# it is added to the global messages list
def register_reply(agent: autogen.ConversableAgent):

    def add_message(recipient, messages, sender, config): 
        last_msg = messages[-1]
        # Check if message has content or function call
        if last_msg.get('content') != '' or last_msg.get('function_call') is not None:
            g_messages.append(messages[-1]) # add last message in the list of messages
            print(messages[-1])
        return False, None  # required to ensure the agent communication flow continues

    agent.register_reply(
        [autogen.Agent, None],
        reply_func=add_message
    )


# Reset messages to start message
def reset_messages():
    g_messages.clear()
    g_messages.append(start_msg)


# Flask route handlers

@app.route('/')
def home():
    return render_template('index.html', messages=g_messages, allow_input=True)


@app.route('/execute', methods=['GET', 'POST'])
def execute():
    # Get instructions from user
    instructions = request.form['instructions']
    if instructions == '':
        instructions = 'Book the cheapest flight from Tokyo to Toronto'

    asyncio.run(execute_task(instructions))
    return render_template('index.html', messages=g_messages, allow_input=False)


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    reset_messages()
    return render_template('index.html', messages=g_messages, allow_input=True)