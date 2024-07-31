"""
Module llm_helper
This module provides the LLMHelper class for managing and executing large language model operations.
"""

import json
import os
import logging
import time
import traceback
from typing import Any, Dict, List, Union
from openai import AzureOpenAI
from promptflow.connections import CustomConnection # type: ignore
import yaml
from .lm_helper import LMHelper


class LLMHelper(LMHelper):
    """
    A class that extends LMHelper for large language models.
    """

    def create_client(self) -> AzureOpenAI:
        """
        Create an Azure OpenAI client.

        Returns:
            AzureOpenAI: The created Azure OpenAI client.
        """
        cnn: CustomConnection = self.custom_connections
        return AzureOpenAI(
            azure_endpoint=str(cnn.configs["llm_api_endpoint"]),
            api_key=str(cnn.secrets["llm_api_key"]),
            api_version=str(cnn.configs["llm_api_version"]),
        )

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """
        Retrieve the list of tools from the topic object.

        Returns:
            List[Dict[str, Any]]: The list of tools.
        """
        # Determine the configuration type
        config_type = "project_config" #self.topic_object.get("config_type", "project_config")

        if config_type == "project_config":
            return self._get_tools_from_project_config()
        elif config_type == "database_config":
            return self._get_tools_from_database_config()
        else:
            raise ValueError(f"Unknown config type: {config_type}")
    
    def _get_tools_from_project_config(self) -> List[Dict[str, Any]]:
        """
        Retrieve the list of tools from the project configuration.

        Returns:
            List[Dict[str, Any]]: The list of tools.
        """
        tools: List[Dict[str, Any]] = self.topic_object["tools"]
        standard_tool_functions: List[str] = self.topic_object["standard_tool_functions"]

        for stf in standard_tool_functions:
            path = os.path.join(os.getcwd(), "standard_tool_functions", stf + ".yaml")
            with open(path, "r", encoding="utf-8") as file:
                tool = yaml.safe_load(file)
            tools.append(tool)

        return tools

    def _get_tools_from_database_config(self) -> List[Dict[str, Any]]:
        """
        Handle the retrieval of tools from the database configuration.

        Returns:
            List[Dict[str, Any]]: The list of tools (empty in this case).
        """
        # Implement database retrieval logic here if needed
        return []
    
    def execute(
        self,
        session_id: str,
        conversation_id: str,
        client: AzureOpenAI,
        model_name: str,
        messages: List[Dict[str, str]],
        tools_list: List[Dict[str, Any]],
        params: Dict[str, float],
        tool_choice: str = "auto",
    ) -> Union[object, None]:
        """
        Executes the language model with provided parameters and logs the success or failure.

        Args:
            session_id (str): The session ID.
            conversation_id (str): The conversation ID.
            client (AzureOpenAI): The Azure OpenAI client.
            model_name (str): The name of the model to use.
            messages (List[Dict[str, str]]): The list of messages to send to the model.
            tools_list (List[Dict[str, Any]]): The list of tools to use.
            params (Dict[str, float]): The parameters for the model.
            tool_choice (str, optional): The tool choice. Defaults to "auto".

        Returns:
            Union[object, None]: The completion object from the language model, or None if an exception occurred.
        """
        start_time: float = time.time()

        try:
            completion: object = None

            if not tools_list:
                # Create a completion without tools
                completion = client.chat.completions.create(
                    messages=messages, # type: ignore
                    model=model_name,
                    temperature=params["temperature"],
                    top_p=params["top_p"],
                    frequency_penalty=params["frequency_penalty"],
                    presence_penalty=params["presence_penalty"],
                    stop=None,
                )
            else:
                # Create a completion with tools
                completion = client.chat.completions.create(
                    messages=messages, # type: ignore
                    model=model_name,
                    temperature=params["temperature"],
                    top_p=params["top_p"],
                    frequency_penalty=params["frequency_penalty"],
                    presence_penalty=params["presence_penalty"],
                    stop=None,
                    tools=tools_list, # type: ignore
                    tool_choice=tool_choice, # type: ignore
                )

            end_time: float = time.time()
            execution_time_ms: float = (end_time - start_time) * 1000

            log_data: Dict[str, Any] = {
                "session_id": str(session_id),
                "conversation_id": str(conversation_id),
                "system_fingerprint": completion.system_fingerprint,  # type: ignore
                "completion_id": completion.id,  # type: ignore
                "utterance": messages[-1]["content"],
                "execution_time_ms": execution_time_ms,	
                "tokens": {
                    "prompt_tokens": completion.usage.prompt_tokens,  # type: ignore
                    "completion_tokens": completion.usage.completion_tokens,  # type: ignore
                    "total_tokens": completion.usage.total_tokens,  # type: ignore
                },                                
            }

            logging.info("Execution completed", extra=log_data)

            return completion

        except Exception as e:
            log_data: Dict[str, Any] = {
                "session_id": str(session_id),
                "conversation_id": str(conversation_id),
                "messages": messages,
                "error": "".join(traceback.format_exception(None, e, e.__traceback__)),
            }
            logging.error("Failure occurred", extra=log_data)

            return None
