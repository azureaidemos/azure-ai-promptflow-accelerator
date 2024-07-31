"""
This code defines a class ConversationDataHelper that manages conversation data, 
saving it to and loading it from JSON files. This class provides functionality 
to get, save, and reset conversation data based on provided conversation parameters.
"""

import json
import os
from typing import Any, Dict

class ConversationDataHelper:
    """
    A helper class for managing conversation data. This class provides methods to 
    retrieve, save, and reset conversation data from/to JSON files stored in a chat.

    Attributes:
        conversation_parameters (dict[str, Any]): Parameters for the conversation.
        _chat_path (str): Path to the chat where conversation data files are stored.
    """
    
    def __init__(self, conversation_parameters: Dict[str, Any]):
        """
        Initializes the ConversationDataHelper with given conversation parameters.

        Args:
            conversation_parameters (dict[str, Any]): Parameters for the conversation.
        """
        self.conversation_parameters: Dict[str, Any] = conversation_parameters
        self._chat_path: str = os.path.join(os.getcwd(), "chats")

    def get_conversation_data(self) -> Dict[str, Any]:
        """
        Retrieves the conversation data. If the data file does not exist, it creates
        a default conversation data file.

        Returns:
            dict[str, Any]: The conversation data.
        """
        file_path: str = self._conversation_data_file_path()

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                conversation_data = json.load(file)
        else:
            conversation_data = {
                "conversation_id": self.conversation_parameters["conversation_id"],
                "topic_name": "default",
            }
            self.save_conversation_data(conversation_data)

        return conversation_data

    def save_conversation_data(self, conversation_data: Dict[str, Any]):
        """
        Saves the conversation data to a JSON file.

        Args:
            conversation_data (dict[str, Any]): The conversation data to be saved.
        """
        file_path: str = self._conversation_data_file_path()
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(conversation_data, file)

    def reset_conversation_data(self) -> None:
        """
        Resets the conversation data to default values.

        Args:
            conversation_data (dict[str, Any]): The conversation data as a dictionary.

        Returns:
            dict[str, Any]: The reset conversation data as a dictionary.
        """
        reset_conversation_data = {
                "conversation_id": self.conversation_parameters["conversation_id"],
                "topic_name": "default",
            }
        self.save_conversation_data(reset_conversation_data)

    def _conversation_data_file_path(self) -> str:
        """
        Constructs and returns the file path for the conversation data file using 
        the conversation ID.

        Returns:
            str: The file path for the conversation data file.
        """
        return os.path.join(
            self._chat_path, self.conversation_parameters["conversation_id"] + ".json"
        )