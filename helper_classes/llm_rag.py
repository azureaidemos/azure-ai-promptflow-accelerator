import json
from typing import Any, Dict, List
from openai import AzureOpenAI
from promptflow.connections import CustomConnection  # type: ignore
from promptflow.connections import CognitiveSearchConnection # type: ignore
from lm_helpers.llm_helper import LLMHelper

class LlmRag:
    """
    A class to handle LLM operations for Q&A.
    """

    def __init__(
        self,
        client: AzureOpenAI,
        custom_connections: CustomConnection,
        cognitive_search_connection: CognitiveSearchConnection,
        conversation_parameters: Dict[str, Any],
        response_value: List[Dict[str, Any]],
        conversation_data: Dict[str, Any],
        topic: Dict[str, Any],
        min_reranker_score: float = 0.0,
        query_key: str = "query",
        score_key: str = "@search.rerankerScore",
        content_key: str = "content"
    ):
        self.response_value = response_value
        self.conversation_data = conversation_data
        self.topic = topic
        self.min_reranker_score = min_reranker_score
        self.client = client
        self.custom_connections = custom_connections
        self.cognitive_search_connection = cognitive_search_connection
        self.conversation_parameters = conversation_parameters
        self.query_key = query_key
        self.score_key = score_key
        self.content_key = content_key

    def execute(self, query: str, previous_answer_provided: str) -> str:
        """
        Executes the LLM query and returns the response.
        """
        chunks = self.get_chunks()
        messages = self.get_messages(chunks, query, previous_answer_provided)
        completion = self.call_llm(messages)
        return str(completion.choices[0].message.content)  # type: ignore

    def call_llm(self, messages: List[Dict[str, str]]) -> object:
        """
        Calls the LLM to process the messages.
        """
        llm_helper = LLMHelper(
            self.custom_connections,
            self.cognitive_search_connection,
            [],
            self.conversation_data["arguments"][self.query_key],
            json.dumps(self.conversation_parameters),
            self.conversation_data
        )

        client = llm_helper.create_client()
        topic_object = llm_helper.load_topic_object()
        tools_list = []
        params = topic_object["llm_parameters"]
        model_name = str(self.custom_connections.configs["llm_model_name"])  # type: ignore

        return llm_helper.execute(
            session_id=self.conversation_parameters["session_id"],
            conversation_id=self.conversation_parameters["conversation_id"],
            client=client,
            model_name=model_name,
            messages=messages,
            tools_list=tools_list,
            params=params
        )

    def get_messages(self, chunks: List[str], query: str, previous_answer_provided: str) -> List[Dict[str, str]]:
        """
        Constructs the messages for the LLM.
        """
        system_prompt = (
            "Answer the User's query using ONLY the information provided below:\n\n" + json.dumps(chunks)
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": previous_answer_provided},
            {"role": "user", "content": query},
        ]
        return messages

    def get_chunks(self) -> List[str]:
        """
        Retrieves the chunks from the response value.

        Returns:
            List[str]: The list of content chunks.
        """
        chunks: List[str] = []
        for item in self.response_value:
            reranker_score = item[self.score_key]
            if reranker_score >= self.min_reranker_score:
                chunks.append(item[self.content_key])
        return chunks
