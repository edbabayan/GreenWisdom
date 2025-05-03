from typing import Generator
from langchain_core.outputs import ChatGenerationChunk
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict
from dotenv import load_dotenv
from src.config import CFG


# Define state
class AgentState(TypedDict):
    query: str
    answer: str

class ChatAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        self.app = self._build_graph()

    def _answer_question(self, state: AgentState) -> AgentState:
        query = state["query"]
        response = self.llm.invoke(query)
        return {"query": query, "answer": response.content}

    def _build_graph(self):
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("answer_node", self._answer_question)
        graph_builder.set_entry_point("answer_node")
        graph_builder.add_edge("answer_node", END)
        return graph_builder.compile()

    def ask(self, query: str) -> AgentState:
        return self.app.invoke({"query": query})

    def stream(self, query: str) -> Generator[str, None, None]:
        for chunk in self.llm.stream(query):
            if isinstance(chunk, ChatGenerationChunk):
                yield chunk.message.content



if __name__ == '__main__':
    # Load environment variables
    load_dotenv(dotenv_path=CFG.env_variable_file)

    chatbot = ChatAgent()
    response = chatbot.ask("What is the capital of France?")
    print(response)