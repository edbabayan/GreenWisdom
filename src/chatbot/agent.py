from typing import Annotated

from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph.message import add_messages

from langgraph.graph import StateGraph, END
from src.config import CFG

# Load environment variables
load_dotenv(dotenv_path=CFG.env_variable_file)

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    streaming=True,
)

# Node function
def answer_question(state: State):
    response = llm.invoke(state["messages"])

    return {"messages": [response]}

# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("answer_node", answer_question)
graph_builder.set_entry_point("answer_node")
graph_builder.add_edge("answer_node", END)
graph = graph_builder.compile()
