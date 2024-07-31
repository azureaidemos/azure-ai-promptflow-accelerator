"""
Module customer_query_handler
This module provides the CustomerQueryHandler class for managing and executing customer queries related to customer information.

Classes:
    CustomerQueryHandler: Handles customer info queries by performing language model operations.
"""
import json
from typing import Any, Dict, List
import yaml
from promptflow.connections import CustomConnection  # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from helper_classes_customer.base_classes.handler_base import HandlerBase
from lm_helpers.llm_helper import LLMHelper

class CustomerQueryHandler(HandlerBase):
    """
    A class that handles customer info queries by managing and executing language model operations.
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
        Executes the customer info query handler.
        """
        customer_info: Dict[str, Any] = self.conversation_data["arguments"]
        email: str = customer_info["email"]
        query: str = customer_info["query"]
 
        # Load customer data from the YAML file and filter based on email
        filtered_object: Dict[str, Any] = self.get_customer_by_email(email)
 
        if not customer_info:
            return self.handle_customer_not_found()
 
 
        customer_response: str = self.get_customer_response(filtered_object, email, query)
        response: str = ""
        if customer_response == "not_found": #TODO: this not happening, we need a better way to handle this.
            response = self.handle_customer_not_found()
        else:
            response = self.handle_customer_found(customer_response)
        return response

    def handle_customer_not_found(self) -> str:
        """
        Handles the case where the customer information is not found.
        """
        self.conversation_data["arguments"]["email"] = None
        self.save_conversation_data()

        return "The customer information was not found. Please provide a valid email address."

    def handle_customer_found(self, customer_response: str) -> str:
        """
        Handles the case where the customer information is found.
        """
        self.conversation_data["arguments"]["customer_response"] = customer_response
        self.save_conversation_data()

        return customer_response

    def get_customers(self) -> List[Dict[str, Any]]:
        """
        Loads the list of customers from the YAML file.
        """
        with open('data/customer_info/sample.yaml', 'r', encoding="utf-8") as file:
            customers = yaml.safe_load(file)
        return customers
    
    def get_customer_by_email(self, email: str) -> Dict[str, Any]:
        """
        Loads the list of customers from the YAML file and filters by email.
        """
        with open('data/customer_info/sample.yaml', 'r', encoding='utf-8') as file:
            customers = yaml.safe_load(file)
            for customer in customers:
                if customer["email"] == email:
                    return customer
        return {}

    def get_customer_response(self, customer_info:  Dict[str, Any], email: str, query: str) -> str:
        """
        Retrieves the customer information from the list of customers based on the email.
        """
        system_prompt: str = ( # type: ignore
            "you are an assistant that identifies customer information from the given email and answers their queries.. "
            + "You must return either the answer from the following json object, or `not_found` if not found. Do not return anything else! The customer's email is {email}.\n\n"
            + json.dumps(customer_info)
        ) 

        user_prompt: str = query
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        completion: object = self.call_llm(messages, query)
        return str(completion.choices[0].message.content)  # type: ignore

    def call_llm(self, messages: List[Dict[str, str]], query: str) -> object:
        """
        Calls the language model to process the messages.
        """
        llm_helper = LLMHelper(
            self.custom_connections,
            self.cognitive_search_connection,
            [], #self.conversation_data["chat_history"]
            query,
            json.dumps(self.conversation_parameters),
            self.conversation_data
        )

        client = llm_helper.create_client()
        topic_object = llm_helper.load_topic_object()
        tools_list = []
        params = topic_object["llm_parameters"]
        model_name = str(self.custom_connections.configs["llm_model_name"])  # type: ignore

        completion = llm_helper.execute(
            session_id=self.conversation_parameters["session_id"],
            conversation_id=self.conversation_parameters["conversation_id"],
            client=client,
            model_name=model_name,
            messages=messages,
            tools_list=tools_list, #type: ignore
            params=params
        )

        return completion
