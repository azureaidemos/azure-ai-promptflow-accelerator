"""
This module provides the ResponseHandler class for handling response messages from a language model
and managing the persistence of function calls to conversation data.

Classes:
    ResponseHandler: A class to handle response messages and manage conversation data.
"""

import json
import logging
from typing import Any, Dict, List, Union
from promptflow.connections import CustomConnection # type: ignore	
from promptflow.connections import CognitiveSearchConnection # type: ignore
from conversation_helper.conversation_data_helper import ConversationDataHelper
from helper_classes_customer.custom_handler import CustomHandler


class ResponseHandler:
    """
    A class to handle response messages from a language model and manage persistence
    of function calls to conversation data.

    Methods:
        handle_response_message: Handles the response message and processes it.
    """
    
    def __init__(
        self,
        conversation_parameters: Dict[str, Any],
        custom_connections: CustomConnection,
        cognitive_search_connection: CognitiveSearchConnection,
        topic: Dict[str, Any],
    ):
        """
        Initializes the ResponseHandler with necessary parameters.

        Args:
            conversation_parameters (Dict[str, Any]): Parameters for the conversation.
            custom_connections (CustomConnection): Custom connections object.
            topic (Dict[str, Any]): The topic object.
        """
        self.topic: Dict[str, Any] = topic
        self.custom_connections: CustomConnection = custom_connections
        self.cognitive_search_connection: CognitiveSearchConnection = cognitive_search_connection
        self.conversation_parameters: Dict[str, Any] = conversation_parameters

    def handle_response_message(
        self,
        first_message: object,
        functions_to_persist: List[str],
        conversation_data: Dict[str, Any],
    ) -> str:
        """
        Handles the response message and processes it.

        Args:
            first_message (object): The first message from the language model.
            functions_to_persist (List[str]): List of functions to persist.
            conversation_data (Dict[str, Any]): Data related to the conversation.

        Returns:
            str: The processed response.
        """
        try:
            processor = self.Processor(
                self.conversation_parameters,
                self.custom_connections,
                self.cognitive_search_connection, # type: ignore
                self.topic,
                first_message,
                functions_to_persist,
                conversation_data,
            )
            return processor.process()

        except Exception as e:
            logging.error("Exception occurred: %s", e)
            return "I'm sorry, I'm having trouble processing your request. Please try again later."

    class Processor:
        """
        A nested class to process response messages and manage function persistence.

        Methods:
            process: Processes the first message and handles function responses.
            process_function_response: Processes a function response from the language model.
            process_function_arguments: Processes the function arguments from the language model response.
            persist_function_to_conversation_data: Persists function arguments to the conversation data if required.
            update_topic_name: Updates the topic name in the conversation data if it has changed.
            process_response_dictionary: Processes the response dictionary from the function arguments.
            process_function_property: Processes the function property from the function arguments.
            update_conversation_data_topicname: Updates the topic name in the conversation data based on property value.
            save_conversation_data: Saves the conversation data using the ConversationDataHelper.
            process_completed_function: Processes the completed function based on the business logic defined in the topic.
        """

        def __init__(
            self,
            conversation_parameters: Dict[str, Any],
            custom_connections: CustomConnection,
            cognitive_search_connection: CognitiveSearchConnection, # type: ignore
            topic: Dict[str, Any],
            first_message: object,
            functions_to_persist: List[str],
            conversation_data: Dict[str, Any],
        ):
            """
            Initializes the Processor with necessary parameters.

            Args:
                conversation_parameters (Dict[str, Any]): Parameters for the conversation.
                custom_connections (CustomConnection): Custom connections object.
                topic (Dict[str, Any]): The topic object.
                first_message (object): The first message from the language model.
                functions_to_persist (List[str]): List of functions to persist.
                conversation_data (Dict[str, Any]): Data related to the conversation.
            """
            self.conversation_parameters: Dict[str, Any] = conversation_parameters
            self.custom_connections: CustomConnection = custom_connections
            self.cognitive_search_connection: CognitiveSearchConnection = cognitive_search_connection
            self.topic: Dict[str, Any] = topic
            self.first_message = first_message
            self.functions_to_persist: List[str] = functions_to_persist
            self.conversation_data = conversation_data

        def process(self) -> str:
            """
            Processes the first message and handles function responses.

            Returns:
                str: The processed response.
            """
            if self.first_message.tool_calls and self.first_message.tool_calls[0].function:  # type: ignore
                return self.process_function_response(self.first_message.tool_calls[0].function)  # type: ignore

            if self.first_message.content is not None:  # type: ignore
                return str(self.first_message.content)  # type: ignore
            else:
                # TODO: will this ever be the case?
                pass
            return ""

        def process_function_response(self, fn: object) -> str:
            """
            Processes a function response from the language model.

            Args:
                fn (object): The function object from the language model response.

            Returns:
                str: The processed response.
            """
            self.persist_function_to_conversation_data(fn)

            fn_args: str = str(fn.arguments)  # type: ignore
            arguments: Dict[str, Any] = json.loads(fn_args)
            return self.process_function_arguments(fn.name, arguments)  # type: ignore
        
        def process_response_dictionary(self, fn_name: str, response: Dict[str, Any]) -> str:
            """
            Processes the response dictionary from the function arguments.

            Args:
                fn_name (str): The name of the function.
                response (Dict[str, Any]): The response dictionary.

            Returns:
                str: The processed response.
            """
            save_conversation_data: bool = self.update_topic_name(response)
            if save_conversation_data:
                self.save_conversation_data()

            completed_response: Union[str, None] = self.process_completed_function(fn_name)
            if isinstance(completed_response, str):
                return completed_response


            if "response" in response:
                return response["response"]


            return "Unknown Function"
        
        def process_function_arguments(
            self, fn_name: str, arguments: Dict[str, Any]
        ) -> str:
            """
            Processes the function arguments from the language model response.

            Args:
                fn_name (str): The name of the function.
                arguments (Dict[str, Any]): The arguments of the function.

            Returns:
                str: The processed response.
            """
            if "response" in arguments:
                # response = str(arguments.get("response"))  # type: ignore
                response: str = self.process_response_dictionary(fn_name, arguments)
                return response

            return self.process_function_property(fn_name, arguments)

        def persist_function_to_conversation_data(self, fn: object) -> None:
            """
            Persists function arguments to the conversation data if required.

            Args:
                fn (object): The function object from the language model response.
            """
            if fn.name in self.functions_to_persist:  # type: ignore
                if "arguments" not in self.conversation_data:
                    self.conversation_data["arguments"] = {}

                fn_args = json.loads(fn.arguments)  # type: ignore
                cd_args: Dict[str, str] = self.conversation_data["arguments"]
                for key, value in fn_args.items():
                    key: str
                    value: str
                    if key != "response":
                        cd_args[key] = value

                self.save_conversation_data()

        def update_topic_name(self, response: Dict[str, Any]) -> bool:
            """
            Updates the topic name in the conversation data if it has changed.

            Args:
                response (Dict[str, Any]): The response dictionary.

            Returns:
                bool: True if the topic name was updated, False otherwise.
            """
            if "response" in response and "topic_name" in response["response"]:
                topic_name: str = response["response"]["topic_name"]
                if self.conversation_data["topic_name"] != topic_name:
                    self.conversation_data["topic_name"] = topic_name
                    return True

            return False

        def process_function_property(
            self, fn_name: str, arguments: Dict[str, Any]
        ) -> str:
            """
            Processes the function property from the function arguments.

            Args:
                fn_name (str): The name of the function.
                arguments (Dict[str, Any]): The arguments of the function.

            Returns:
                str: The processed response.
            """
            return_message: str = ""
            _, property_value = list(arguments.items())[0]

            cd_is_dirty = self.update_conversation_data_topicname(property_value)
            if "response" in property_value:
                return_message = property_value["response"]

            if cd_is_dirty:
                self.save_conversation_data()

            completed_response: Union[str, None] = self.process_completed_function(fn_name)
            if isinstance(completed_response, str):
                return completed_response

            return return_message

        def update_conversation_data_topicname(
            self, property_value: Dict[str, Any]
        ) -> bool:
            """
            Updates the topic name in the conversation data if it has changed based on property value.

            Args:
                property_value (Dict[str, Any]): The property value.

            Returns:
                bool: True if the topic name was updated, False otherwise.
            """
            if "topic_name" in property_value:
                topic_name: str = property_value["topic_name"]
                if self.conversation_data["topic_name"] != topic_name:
                    self.conversation_data["topic_name"] = topic_name
                    return True
            return False

        def save_conversation_data(self):
            """
            Saves the conversation data using the ConversationDataHelper.
            """
            cd_helper: ConversationDataHelper = ConversationDataHelper(
                self.conversation_data
            )
            cd_helper.save_conversation_data(self.conversation_data)

        def process_completed_function(self, fn_name: str) -> Union[str, None]:
            """
            Processes the completed function based on the business logic defined in the topic.

            Args:
                fn_name (str): The name of the function.

            Returns:
                Union[str, None]: The processed response or None.
            """
            topic_business_logic: List[Dict[str, Any]] = self.topic.get(
                "follow_on_business_logic", []
            )
            # This searches the list of business logic rules to find a rule that matches the given function name (fn_name). 
            # If found, it assigns the rule to business_logic_for_function, otherwise, it assigns None.
            business_logic_for_function: Union[Dict[str, Any], None] = next(
                (obj for obj in topic_business_logic if obj["name"] == fn_name), None)
            
            # Check for Valid Action
            # If no matching business logic is found or if the "action" key is missing 
            # in the found rule, the method returns None.
            if (not business_logic_for_function or "action" not in business_logic_for_function):
                return None

            action: Dict[str, Any] = business_logic_for_function["action"]
            action_type: str = action.get("type", "")
            if action_type == "custom_handler":
                method_name: str = action.get("method_name", "")
                ch: CustomHandler = CustomHandler(
                    self.conversation_parameters,
                    self.custom_connections,
                    self.cognitive_search_connection, # type: ignore
                    self.conversation_data,
                    self.topic,
                )
                method = getattr(ch, method_name)
                return method()
