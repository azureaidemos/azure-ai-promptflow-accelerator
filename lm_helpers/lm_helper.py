"""
Module lm_helper
This module provides the abstract base class LMHelper for managing and executing language model operations.
"""

from abc import ABC, abstractmethod
import json
import os
import logging
from typing import Any, Dict, List, Union
import yaml
from promptflow.connections import CustomConnection # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore

class LMHelper(ABC):
    """
    Abstract base class for managing and executing language model operations.
    """

    def __init__(
        self,
        custom_connections: CustomConnection,
        cognitive_search_connection: CognitiveSearchConnection,
        chat_history: List[Dict[str, str]],
        query: str,
        conversation_parameters: str,
        conversation_data: Dict[str, str],
    ):
        """
        Initialize the LMHelper with necessary parameters.
        
        Args:
            custom_connections (CustomConnection): Custom connections object.
            chat_history (List[Dict[str, str]]): List of chat history records.
            query (str): The user's query.
            conversation_parameters (str): JSON string of conversation parameters.
            conversation_data (Dict[str, str]): Data related to the conversation.
        """
        self.custom_connections: CustomConnection = custom_connections
        self.cognitive_search_connection: CognitiveSearchConnection = cognitive_search_connection
        self.chat_history: List[Dict[str, str]] = chat_history
        self.query: str = query
        self.conversation_parameters: Dict[str, str] = json.loads(conversation_parameters)
        self.conversation_data: Dict[str, str] = conversation_data
        self.topic_object: Dict[str, Any] = {}

    @abstractmethod
    def create_client(self) -> Any:
        """
        Abstract method to create a client for the language model.

        Returns:
            Any: The created client object.
        """
        pass

    @abstractmethod
    def execute(
        self,
        session_id: str,
        conversation_id: str,
        client: Any,
        model_name: str,
        messages: List[Dict[str, str]],
        tools_list: List[Dict[str, Any]],
        params: Dict[str, float],
        tool_choice: str = "auto",
    ) -> Union[object, None]:
        """
        Abstract method to execute the language model operation.

        Args:
            session_id (str): The session ID.
            conversation_id (str): The conversation ID.
            client (Any): The client object.
            model_name (str): The name of the model to use.
            messages (List[Dict[str, str]]): The list of messages to send to the model.
            tools_list (List[Dict[str, Any]]): The list of tools to use.
            params (Dict[str, float]): The parameters for the model.
            tool_choice (str, optional): The tool choice. Defaults to "auto".

        Returns:
            Union[object, None]: The completion object from the language model, or None if an exception occurred.
        """
        pass

    def load_topic_object(self) -> Dict[str, Any]:
        """
        Load the topic object from a JSON file based on conversation parameters.
        
        Returns:
            Dict[str, Any]: The loaded topic object.
        """
        persona_name: str = self.conversation_parameters["persona_name"]
        topic_area: str = self.conversation_parameters["topic_area"]
        topic_file: str = self.conversation_data["topic_name"] + ".yaml"

        path: str = os.path.join(
            os.getcwd(),
            "persona-" + persona_name,
            "topic_area_" + topic_area,
            topic_file,
        )

        with open(path, "r", encoding="utf-8") as file:
            self.topic_object = yaml.safe_load(file)

        return self.topic_object

    def get_prompt_messages(self) -> List[Dict[str, str]]:
        """
        Construct the prompt messages for the language model based on the topic object and chat history.
        
        Returns:
            List[Dict[str, str]]: The list of prompt messages.
        """
        system_prompt: str = self.get_system_prompt_message()
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

        for chat in self.chat_history:
            messages.append({"role": "user", "content": chat["inputs"]["query"]})  # type: ignore
            messages.append(
                {
                    "role": "assistant",
                    "content": self.get_assistant_message(
                        chat["outputs"]["answer"]  # type: ignore
                    ),
                }
            )

        messages.append({"role": "user", "content": self.query})

        return messages

    def get_assistant_message(self, msg: str) -> str:
        """
        Retrieve the assistant's message from chat history, handling any JSON formatting.
        
        Args:
            msg (str): The assistant's message.
        
        Returns:
            str: The processed assistant's message.
        """
        if not (msg.startswith("{") and msg.endswith("}")):
            return msg

        try:
            json_msg: Dict[str, Any] = json.loads(msg)
            if "response_items" in json_msg:
                response_items = json_msg.get("response_items", [])
                response_item = next(
                    (item for item in response_items if item.get("key") == "response"),
                    None,
                )
                if response_item:
                    return response_item.get("value")

            return msg

        except json.JSONDecodeError as e:
            logging.error("Error logging invalid PF parameters: %s, msg: %s", e, msg)
            return msg

    def get_system_prompt_message(self) -> str:
        """
        Construct the system prompt message for the language model.
        
        Returns:
            str: The system prompt message.
        """
        system_prompt: str = self.topic_object["systemPrompt"] + " \n"
        system_prompt += "Only use the functions you have been provided with. \n"
        system_prompt += "Known details for each function can be found in the JSON object provided. \n"
        system_prompt += json.dumps(self.conversation_data) + " \n\n"
        system_prompt += self.get_safety_prompt() + " \n\n"
        system_prompt += (
            "Your response must be in the language defined by the locale `"
            + self.conversation_parameters["locale"]
            + "`."
        )

        return system_prompt

    def get_safety_prompt(self) -> str:
        """
        Retrieve the content safety system prompt from a file.
        
        Returns:
            str: The content safety system prompt.
        """
        with open("content_safety_system_prompt.txt", "r", encoding="utf-8") as file:
            data = file.read()

        return data
