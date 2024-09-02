from typing import Any
from promptflow.connections import CustomConnection # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from helper_classes.helper_classes_customer.base_classes.handler_base import HandlerBase


class offerDetailHandler(HandlerBase):
    def __init__(
        self,
        conversation_parameters: dict[str, Any],
        custom_connections: CustomConnection,
        cognitive_search_connection: CognitiveSearchConnection,
        conversation_data: dict[str, Any],
        topic: dict[str, Any],
    ):
        super().__init__(conversation_parameters,custom_connections, cognitive_search_connection, conversation_data, topic)


    def execute(self) -> str:
        offer_type: str = self.conversation_data["arguments"]["offer"]
        prefix = "" if offer_type == "NewiPhone" else "Free data and free speaker are limited to first 50 orders this month!."
        response: str = f"{prefix}For more details on  your chosen offer, go to our website https://{offer_type}.vodafone.com. Is there anything else I can do for you today?"

        return response

