"""
This module provides the HandlerBase class for handling conversation parameters,
custom connections, conversation data, and module interactions.

Classes:
    HandlerBase: A base class for handling conversation operations and responses.
"""

from typing import Any
import logging
from openai import AzureOpenAI
from promptflow.connections import CustomConnection # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from conversation_helper.conversation_data_helper import ConversationDataHelper


class HandlerBase:
    """
    A base class for handling conversation operations and responses.

    Attributes:
        conversation_parameters (dict): The dictionary of conversation parameters.
        custom_connections (CustomConnection): The custom connection object.
        conversation_data (dict): The dictionary of conversation data.
        topic (dict): The dictionary of topic data.
    """

    def __init__(
        self,
        conversation_parameters: dict[str, Any],
        custom_connections: CustomConnection,
        cognitive_search_connection: CognitiveSearchConnection,
        conversation_data: dict[str, Any],
        topic: dict[str, Any],
    ):
        """
        Initializes the HandlerBase with the provided parameters.

        Args:
            conversation_parameters (dict): The dictionary of conversation parameters.
            custom_connections (CustomConnection): The custom connection object.
            conversation_data (dict): The dictionary of conversation data.
            topic (dict): The dictionary of topic data.
        """
        self.conversation_parameters = conversation_parameters
        self.conversation_data = conversation_data
        self.custom_connections = custom_connections
        self.cognitive_search_connection = cognitive_search_connection
        self.topic = topic

    def reset_conversation_id(self) -> None:
        """
        Resets the conversation ID by adding a reset response item.
        """        
        logging.info("Resetting conversation ID")
        cd_helper = ConversationDataHelper(self.conversation_data)
        cd_helper.reset_conversation_data()

    def create_llm_client(self) -> AzureOpenAI:
        """
        Creates an AzureOpenAI client using the custom connection configurations.

        Returns:
            AzureOpenAI: The created AzureOpenAI client.
        """
        cnn = self.custom_connections
        return AzureOpenAI(
            azure_endpoint=str(cnn.configs["llm_api_endpoint"]),
            api_key=str(cnn.secrets["llm_api_key"]),
            api_version=str(cnn.configs["llm_api_version"]),
        )

    def save_conversation_data(self) -> None:
        """
        Saves the conversation data using the ConversationDataHelper.
        """
        cd_helper = ConversationDataHelper(self.conversation_data)
        cd_helper.save_conversation_data(self.conversation_data)
