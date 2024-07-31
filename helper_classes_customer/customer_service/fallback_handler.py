from typing import Any
from promptflow.connections import CustomConnection # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from helper_classes_customer.base_classes.handler_base import HandlerBase


class FallbackHandler(HandlerBase):

    def __init__(
        self,
        conversation_parameters: dict[str, Any],
        custom_connections: CustomConnection,
        cognitive_search_connection: CognitiveSearchConnection,
        conversation_data: dict[str, Any],
        topic: dict[str, Any],
    ):
        super().__init__(
            conversation_parameters, custom_connections, cognitive_search_connection, conversation_data, topic
        )

    def execute(self) -> str:

        # confirm_change_to_something_else: bool = self.conversation_data["arguments"][
        #     "confirm_change_to_something_else"
        # ]
        # response: str = ""

        # if not confirm_change_to_something_else:
        #     response = "Okay, let's continue"

        # else:
        response = "Okay, let's return to the top and start again."
        self.reset_conversation_id()

        return response
