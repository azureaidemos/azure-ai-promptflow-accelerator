"""
This module provides a class for validating conversation parameters.

Classes:
    ConversationValidator: A class to validate conversation parameters.
"""

import json
import uuid
import logging

class ConversationValidator:
    """
    A class to validate conversation parameters.

    Attributes:
        params (dict): The dictionary of conversation parameters.
    """

    def __init__(self, conversation_parameters: str):
        """
        Initializes the ConversationValidator with conversation parameters.

        Args:
            conversation_parameters (str): A JSON string of conversation parameters.
        """
        self.params = json.loads(conversation_parameters)

    def validate(self) -> bool:
        """
        Validates the conversation parameters.

        Checks for required parameters and ensures they have valid values and formats.

        Returns:
            bool: True if all required parameters are valid, False otherwise.
        """
        required_params = ["session_id", "conversation_id", "locale", "persona_name"]
        for param in required_params:
            if not self.has_value(param):
                logging.error("Missing required parameter: %s", param.capitalize())
                return False

        guid_params = ["session_id", "conversation_id"]
        for param in guid_params:
            if not self.is_guid(param):
                logging.error("Invalid GUID parameter: %s", param.capitalize())
                return False

        return True

    def has_value(self, parameter_name: str) -> bool:
        """
        Checks if a parameter has a non-empty value.

        Args:
            parameter_name (str): The name of the parameter to check.

        Returns:
            bool: True if the parameter has a non-empty value, False otherwise.
        """
        parameter_value = self.params.get(parameter_name)
        return parameter_value is not None and parameter_value.strip() != ""

    def is_guid(self, parameter_name: str) -> bool:
        """
        Checks if a parameter is a valid GUID.

        Args:
            parameter_name (str): The name of the parameter to check.

        Returns:
            bool: True if the parameter is a valid GUID, False otherwise.
        """
        parameter_value = self.params[parameter_name]
        try:
            uuid.UUID(parameter_value)
            return True
        except ValueError:
            return False
