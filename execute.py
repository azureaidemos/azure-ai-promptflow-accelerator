import json
from typing import Any
from promptflow.core import tool # type: ignore
from promptflow.connections import CustomConnection # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from helper_classes.conversation_helper.conversation_data_helper import ConversationDataHelper
from helper_classes.response_handler import ResponseHandler
from helper_classes.lm_helpers.llm_helper import LLMHelper


@tool
def execute(
    custom_connections: CustomConnection,
    cognitive_search_connection: CognitiveSearchConnection,
    conversation_parameters: str,
    chat_history: list[dict[str, str]],
    query: str,
) -> str:
    """
    Main function to execute the PromptFlow module.

    Args:
        custom_connections (CustomConnection): The custom connections object.
        conversation_parameters (str): The conversation parameters passed to PF.
        chat_history (list[dict[str, str]]): The chat history.
        query (str): The user's query.

    Returns:
        str: This is the response str that will be returned to the user.
    """
    print(cognitive_search_connection)
    # Parse conversation parameters from JSON string to dictionary
    conv_parameters: dict[str, Any] = json.loads(conversation_parameters)

    # Initialize ConversationDataHelper with parsed parameters
    conv_data_helper: ConversationDataHelper = ConversationDataHelper(conv_parameters)
    # Retrieve conversation data
    conv_dict: dict[str, Any] = conv_data_helper.get_conversation_data()

    # Initialize LLMHelper with necessary arguments
    # # # Initialize LLMHelper with necessary arguments
    llm_helper: LLMHelper = LLMHelper(
        custom_connections, cognitive_search_connection, chat_history, query, conversation_parameters, conv_dict
    )
    # Initialize the client
    client = llm_helper.create_client()

    # Load topic object
    topic_object = llm_helper.load_topic_object()

    # Get prompt messages
    messages = llm_helper.get_prompt_messages()

    # Get tools list
    tools_list = llm_helper.get_tools_list()

    # Get model parameters
    params = topic_object["llm_parameters"]

    # Get model name from custom connections
    model_name = str(custom_connections.configs["llm_model_name"])

    # Execute the language model helper and get the first message
    completion: object = llm_helper.execute(
        session_id=conv_parameters["session_id"],
        conversation_id=conv_parameters["conversation_id"],
        client=client,
        model_name=model_name,
        messages=messages,
        tools_list=tools_list,
        params=params
    )

    first_choice_message: object = completion.choices[0].message  # type: ignore

    handler: ResponseHandler = ResponseHandler(conv_parameters, custom_connections, cognitive_search_connection, topic_object)
    
    # Get the list of functions to persist from the topic object
    functions_to_persist: list[str] = topic_object["functions_to_persist"]

    # Handle the response message and return the result
    return handler.handle_response_message(first_choice_message, functions_to_persist, conv_dict)