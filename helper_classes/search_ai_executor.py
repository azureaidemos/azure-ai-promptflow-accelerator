"""
This module provides a class for executing search AI requests.

Classes:
    SearchAiExecutor: A class to execute search AI requests and log the results.
"""

import json
import logging
from typing import Any, Union
import uuid
import traceback
import requests

class SearchAiExecutor:
    """
    A class to execute search AI requests and log the results.

    Attributes:
        endpoint (str): The endpoint URL for the search AI request.
        headers (dict): The headers for the search AI request.
        payload (dict): The payload for the search AI request.
        session_id (uuid.UUID): The session ID for the request.
        conversation_id (uuid.UUID): The conversation ID for the request.
    """

    def __init__(self, endpoint: str, headers: dict[str, str], payload: dict[str, Any], session_id: uuid.UUID, conversation_id: uuid.UUID):
        """
        Initializes the SearchAiExecutor with the provided parameters.

        Args:
            endpoint (str): The endpoint URL for the search AI request.
            headers (dict): The headers for the search AI request.
            payload (dict): The payload for the search AI request.
            session_id (uuid.UUID): The session ID for the request.
            conversation_id (uuid.UUID): The conversation ID for the request.
        """
        self.endpoint: str = endpoint
        self.headers: dict[str, str] = headers
        self.payload: dict[str, Any] = payload
        self.session_id: uuid.UUID = session_id
        self.conversation_id: uuid.UUID = conversation_id

    def execute(self) -> Union[requests.Response, None]:
        """
        Executes the search AI request and logs the results.

        Returns:
            Union[requests.Response, None]: The response from the search AI request, or None if an exception occurred.
        """

        try:
            response: requests.Response = requests.post(
                self.endpoint,
                headers=self.headers,
                data=json.dumps(self.payload),
                timeout=30
            )

            success: bool = response.status_code == 200
            error_message: str = response.reason if not success else ""

            log_data = {
                "session_id": str(self.session_id),
                "conversation_id": str(self.conversation_id),
                "payload": self.payload,
                "success": success,
                "error_message": error_message
            }

            logging.info("Execution completed", extra=log_data)

            return response

        except Exception as e:
            log_data = {
                "session_id": str(self.session_id),
                "conversation_id": str(self.conversation_id),
                "payload": self.payload,
                "error": "".join(traceback.format_exception(None, e, e.__traceback__))
            }
            logging.error("Failure occurred", extra=log_data)

            return None
