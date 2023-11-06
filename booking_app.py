from plugins.CosmosPlugin import CosmosPlugin
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
    cosmos_plugin = kernel.import_skill(CosmosPlugin(cosmos_conn_str), skill_name='CosmosPlugin')
    time_skill = kernel.import_skill(TimeSkill(), skill_name='TimeSkill')

    logging.info('Plugins registered.')

    llm_config = {
        'type': 'azure',
        'azure_deployment': deployment,
        'azure_api_key': api_key,
        'azure_endpoint': endpoint
    }

    planner = AutoGenPlanner(kernel, llm_config=llm_config)

    assistant = planner.create_assistant_agent('Assistant')
    worker = planner.create_user_agent('Worker', max_auto_reply=4, human_input='NEVER')

    logging.info('Planner ready.')

    task = 'What date is today? Are there any flights from Tokyo to Toronto in the near future?'
    worker.initiate_chat(assistant, message=task)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())