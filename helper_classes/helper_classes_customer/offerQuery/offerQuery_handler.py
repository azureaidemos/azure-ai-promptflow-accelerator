"""
Module offer_query_handler
This module provides the OfferQueryHandler class for managing and executing offer queries.
"""

import json
from typing import Any, Dict, List
from promptflow.connections import CustomConnection  # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from helper_classes.helper_classes_customer.base_classes.handler_base import HandlerBase
from helper_classes.lm_helpers.llm_helper import LLMHelper


class OfferQueryHandler(HandlerBase):
    """
    A class that handles offer queries by managing and executing language model operations.
    """

    def __init__(
        self,
        conversation_parameters: Dict[str, Any],
        custom_connections: CustomConnection,
        cognitive_search_connection: CognitiveSearchConnection,        
        conversation_data: Dict[str, Any],
        topic: Dict[str, Any],
    ):
        super().__init__(conversation_parameters, custom_connections, cognitive_search_connection, conversation_data, topic)

    def execute(self) -> str:
        """
        Executes the offer query handler.
        """
        address: Dict[str, Any] = self.conversation_data["arguments"]
        first_line: str = address["first_line"]
        city: str = address["city"]
        postcode: str = address["postcode"]

        json_list_of_addresses: List[Dict[str, str]] = self.get_addresses(postcode)

        cuid: str = self.get_users_cuid(
            json_list_of_addresses, first_line, city, postcode
        )
        response: str = ""
        if cuid == "not_found":
            response = self.handle_cuid_not_found()
        else:
            response = self.handle_cuid_found(cuid)
        return response

    def handle_cuid_not_found(self) -> str:
        """
        Handles the case where the CUID is not found.
        """
        address: Dict[str, Any] = self.conversation_data["arguments"]
        address["first_line"] = None
        address["city"] = None
        address["postcode"] = None

        business_logic: List[Dict[str, Any]] = self.topic["follow_on_business_logic"]
        current_topic_name: str = str(
            list(
                filter(lambda obj: obj["name"] == "get_user_address", business_logic)  # type: ignore
            )[0]["current_topic_name"]
        )

        self.conversation_data["topic_name"] = current_topic_name
        self.save_conversation_data()
        
        return "The address is not found, please re-enter it."

    def handle_cuid_found(self, cuid: str) -> str:
        """
        Handles the case where the CUID is found.
        """
        self.conversation_data["arguments"]["cuid"] = cuid
        self.save_conversation_data()

        api_response: List[Dict[str, str]] = [
            {"NewiPhone": "Brand new Iphone twice as cheap as in the store!"},
            {"FreeDataForever": "Free data for life!"},
            {"FreeSpeaker": "Get a free speaker with your next contract!"},
        ]

        values: List[str] = [list(offer.values())[0] for offer in api_response]
        comma_separated_values: str = ", ".join(values)

        return "What offer are you interested in? " + comma_separated_values

    def get_addresses(self, postcode: str) -> List[Dict[str, str]]:
        """
        Calls an API to get addresses from the postcode.
        """
        api_response: List[Dict[str, str]] = [
            {"cuid": "1", "address": "1 Some Street, Derby, " + postcode},
            {"cuid": "2", "address": "2 Some Street, Derby, " + postcode},
            {"cuid": "3a", "address": "3a Some Street, Derby, " + postcode},
            {"cuid": "3b", "address": "3b Some Street, Derby, " + postcode},
            {"cuid": "4", "address": "4 Some Street, Derby, " + postcode},
            {"cuid": "5", "address": "5 Some Street, Derby, " + postcode},
        ]
        return api_response

    def get_users_cuid(
        self,
        json_list_of_addresses: List[Dict[str, str]],
        first_line: str,
        city: str,
        postcode: str,
    ) -> str:
        """
        Retrieves the user's CUID from the list of addresses.
        """
        system_prompt: str = (
            "you are an assistant that identifies the customer ID number from the address given. "
            + "You must return either the correct `cuid` from the following json object, or `not_found` if not found. Do not return anything else!\n\n"
            + json.dumps(json_list_of_addresses)
        )

        user_prompt: str = (
            "I live at " + first_line + ", " + city + ", " + postcode + ". "
        )
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        completion: object = self.call_llm(messages)
        return str(completion.choices[0].message.content)  # type: ignore

    def call_llm(self, messages: List[Dict[str, str]]) -> object:
        """
        Calls the language model to process the messages.
        """
        llm_helper = LLMHelper(
            self.custom_connections,
            self.cognitive_search_connection,
            self.conversation_data["chat_history"],
            self.conversation_data["query"],
            json.dumps(self.conversation_parameters),
            self.conversation_data
        )

        client = llm_helper.create_client()
        topic_object = llm_helper.load_topic_object()
        tools_list = llm_helper.get_tools_list()
        params = topic_object["llm_parameters"]
        model_name = str(self.custom_connections.configs["llm_model_name"])  # type: ignore

        completion = llm_helper.execute(
            session_id=self.conversation_parameters["session_id"],
            conversation_id=self.conversation_parameters["conversation_id"],
            client=client,
            model_name=model_name,
            messages=messages,
            tools_list=tools_list,
            params=params
        )

        return completion
