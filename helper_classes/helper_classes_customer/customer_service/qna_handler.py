"""
Module qna_handler
This module provides the QnaHandler class for managing and executing Q&A operations.

Classes:
    QnaHandler: Handles Q&A related tasks by performing AI search and language model operations.
"""

import json
from typing import Any, Dict
from promptflow.connections import CustomConnection  # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from helper_classes.ai_search import AiSearch
from helper_classes.llm_rag import LlmRag
from helper_classes.helper_classes_customer.base_classes.handler_base import HandlerBase

class QnaHandler(HandlerBase):
    """
    This class represents a Q&A handler for customer service.
    It handles the execution of Q&A related tasks and generates a string response.

    Args:
        conversation_parameters (Dict[str, Any]): The conversation parameters.
        custom_connections (CustomConnection): The custom connections.
        conversation_data (Dict[str, Any]): The conversation data.
        topic (Dict[str, Any]): The topic.
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
        Executes the Q&A handler and generates a string response.

        Returns:
            str: The generated response.
        """
        # Extract AI search configuration from topic
        ai_search_config = self.topic["follow_on_business_logic"][0]["ai_search"]

        # Perform AI search
        ai_search = AiSearch(self.conversation_data, self.conversation_parameters, ai_search_config, self.cognitive_search_connection)
        response = ai_search.execute()
        min_reranker_score = ai_search.search_params.get("min_reranker_score")
        query_key = ai_search.search_params.get("query_key")
        score_key = ai_search.search_params.get("score_key")
        content_key = ai_search.search_params.get("content_key")
        llm_response = ""

        # Check for a successful response
        if not response or response.status_code != 200:
            # TODO: Handle error
            pass
        else:
            response_data = json.loads(response.text)
            response_value = response_data["value"]
            query = self.conversation_data["arguments"]["query"]
            previous_answer_provided = self.conversation_data["arguments"].get("previous_answer_provided", "")



            llm = LlmRag(
                self.create_llm_client(),
                self.custom_connections,
                self.cognitive_search_connection,
                self.conversation_parameters,
                response_value,
                self.conversation_data,
                self.topic,
                min_reranker_score,
                query_key,
                score_key,
                content_key
            )
            llm_response = llm.execute(query, previous_answer_provided)

        return llm_response
