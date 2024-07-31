"""
Module: CustomHandler
This module contains the CustomHandler class, which handles various customer-related queries
using specific handlers for QnA, offer queries, offer details, fallback scenarios, and customer queries.

Classes:
    CustomHandler: Handles various customer queries by utilizing appropriate handlers.

Dependencies:
    typing: For type hinting.
    logging: For logging errors and other information.
    promptflow.connections.CustomConnection: For handling custom connections.
    helper_classes_customer.customer_service.qna_handler.QnaHandler: For handling QnA queries.
    helper_classes_customer.offerQuery.offerQuery_handler.OfferQueryHandler: For handling offer queries.
    helper_classes_customer.offerQuery.offerDetail_handler.offerDetailHandler: For handling offer details.
    helper_classes_customer.customer_service.fallback_handler.FallbackHandler: For handling fallback scenarios.
    helper_classes_customer.customer_service.customerQuery_handler.CustomerQueryHandler: For handling customer queries.
"""

from typing import Any, Dict
import logging
from promptflow.connections import CustomConnection  # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from helper_classes_customer.customer_service.qna_handler import QnaHandler
from helper_classes_customer.customer_service.fallback_handler import FallbackHandler
from helper_classes_customer.customer_service.customerQuery_handler import CustomerQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomHandler:
    """
    CustomHandler class to handle various customer-related queries.
    
    Methods:
        handle_qna: Handles QnA queries.
        handle_offerQuery: Handles offer queries.
        handle_offerDetail: Handles offer detail queries.
        handle_fallback: Handles fallback scenarios.
        handle_customer_query: Handles customer queries.
    """

    def __init__(
        self,
        conversation_parameters: Dict[str, Any],
        custom_connections: CustomConnection,
        cognitive_search_connection: CognitiveSearchConnection,
        conversation_data: Dict[str, Any],
        topic: Dict[str, Any],
    ):
        """
        Initializes the CustomHandler with conversation parameters, custom connections,
        conversation data, and the topic.
        
        Args:
            conversation_parameters (Dict[str, Any]): Parameters for the conversation.
            custom_connections (CustomConnection): Custom connections for the handler.
            conversation_data (Dict[str, Any]): Data related to the conversation.
            topic (Dict[str, Any]): Topic of the conversation.
        """
        self.conversation_parameters = conversation_parameters        
        self.conversation_data = conversation_data
        self.custom_connections = custom_connections
        self.cognitive_search_connection = cognitive_search_connection
        self.topic = topic

    def handle_qna(self) -> str:
        """Handles QnA queries using QnaHandler."""
        try:
            handler = QnaHandler(
                self.conversation_parameters,
                self.custom_connections,
                self.cognitive_search_connection,
                self.conversation_data,
                self.topic,
            )
            return handler.execute()
        except Exception as e:
            logger.error("Exception occurred: %s", e)
            raise

    def handle_fallback(self) -> str:
        """Handles fallback scenarios using FallbackHandler."""
        try:
            handler = FallbackHandler(
                self.conversation_parameters,
                self.custom_connections,
                self.cognitive_search_connection,
                self.conversation_data,
                self.topic,
            )
            return handler.execute()
        except Exception as e:
            logger.error("Exception occurred: %s", e)
            raise

    def handle_customerQuery(self) -> str:
        """Handles customer queries using CustomerQueryHandler."""
        try:
            handler = CustomerQueryHandler(
                self.conversation_parameters,
                self.custom_connections,
                self.cognitive_search_connection,
                self.conversation_data,
                self.topic,
            )
            return handler.execute()
        except Exception as e:
            logger.error("Exception occurred: %s", e)
            raise
