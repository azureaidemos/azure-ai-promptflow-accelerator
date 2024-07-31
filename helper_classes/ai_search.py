from typing import Any, Dict, Union
import requests
from helper_classes.search_ai_executor import SearchAiExecutor
from promptflow.connections import CognitiveSearchConnection # type: ignore

class AiSearch:
    """
    Encapsulates the AI search logic.
    """

    def __init__(self, conversation_data: Dict[str, Any], conversation_parameters: Dict[str, Any], ai_search_config: Dict[str, Any], cognitive_search_connection: CognitiveSearchConnection):
        self.conversation_data = conversation_data
        self.conversation_parameters = conversation_parameters
        self.index_details = ai_search_config["index_details"]
        self.search_params = ai_search_config["parameters"]
        self.cognitive_search_connection = cognitive_search_connection

    def execute(self) -> Union[requests.Response, None]:
        """
        Executes the AI search with the configured parameters.

        Returns:
            Union[requests.Response, None]: The response from the AI search.
        """
        payload = self.get_payload()
        endpoint = self.get_endpoint()
        headers = self.get_headers()

        # Make the request
        executor = SearchAiExecutor(
            endpoint,
            headers,
            payload,
            self.conversation_parameters["session_id"],
            self.conversation_parameters["conversation_id"],
        )
        return executor.execute()

    def get_payload(self) -> Dict[str, Any]:
        """
        Constructs the payload for the AI search request.

        Returns:
            Dict[str, Any]: The payload for the AI search request.
        """
        query = self.conversation_data["arguments"]["query"]

        # Extract parameters from the ai_search_parameters dictionary
        select = self.search_params.get("select", "content")
        chunk_count = self.search_params.get("k", 5)
        semantic_configuration = self.search_params.get("semantic_configuration", "default")
        vector_field = self.search_params.get("vector_field", "contentVector")
        query_type = self.search_params.get("query_type", "semantic")
        query_language = self.search_params.get("query_language", "en-GB")

        payload = {
            "search": query,
            "select": select,
            "vectorQueries": [
                {
                    "kind": "text",
                    "text": query,
                    "fields": vector_field,
                    "k": chunk_count,
                }
            ],
            "queryType": query_type,
            "semanticConfiguration": semantic_configuration,
            "queryLanguage": query_language,
            "top": chunk_count,
        }
        return payload

    def get_endpoint(self) -> str:
        """
        Constructs the endpoint URL for the AI search.

        Returns:
            str: The endpoint URL for the AI search.
        """
        service_name = self.index_details["service_name"]
        index_name = self.index_details["index_name"]
        return f"https://{service_name}.search.windows.net/indexes/{index_name}/docs/search?api-version=2024-05-01-Preview"

    def get_headers(self) -> Dict[str, str]:
        """
        Constructs the headers for the AI search request.

        Returns:
            Dict[str, str]: The headers for the AI search request.
        """
        api_key = self.cognitive_search_connection.api_key
        
        if api_key is None:
            raise ValueError("Azure AI Search API key is missing. Please provide a valid API key.")
        
        return {
            "Content-Type": "application/json",
            "api-key": api_key,  # type: ignore
        }
