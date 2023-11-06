from plugins.FlightsPlugin import FlightsPlugin
from semantic_kernel.core_skills import TimeSkill
from semantic_kernel.connectors.ai.open_ai import AzureTextCompletion
from planning.autogen_planner import AutoGenPlanner
import semantic_kernel as sk
import logging
from dotenv import load_dotenv
import os

async def main():

    # Load environment variables from `.env` file
    load_dotenv()

    # Instantiate kernel
    kernel = sk.Kernel()

    # Prepare Azure OpenAI service using credentials stored in the `.env` file
    deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
    kernel.add_text_completion_service('gpt-4', AzureTextCompletion(deployment, endpoint, api_key))

    logging.info('Kernel loaded.')

    # Register plugins
    cosmos_conn_str = os.getenv('COSMOS_CONNECTION_STRING')
    cosmos_plugin = kernel.import_skill(FlightsPlugin(cosmos_conn_str), skill_name='FlightsPlugin')
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

    # Start chat

    worker.initiate_chat(booking_agent, message='Book the cheapest flight from Tokyo to Toronto.')


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())