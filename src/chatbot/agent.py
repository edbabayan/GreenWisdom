import os
from typing import Annotated, TypedDict, List

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, END
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.tools import tool

from src.chatbot.prompts import MultiAgentPrompts
from src.config import CFG

# Load environment variables from the configuration file
load_dotenv(dotenv_path=CFG.env_variable_file)


class State(TypedDict):
    """State schema for the conversation graph.

    Attributes:
        messages: List of messages in the conversation, with auto-aggregation
                 of responses using add_messages annotation.
    """
    messages: Annotated[List[BaseMessage], add_messages]


# Initialize the language model with streaming enabled
llm = ChatOpenAI(
    model=CFG.llm_model,
    streaming=True,
    temperature=0.0  # More deterministic responses
)

# Initialize Tavily search tool for web searching
search_tavily = TavilySearch(
    max_results=CFG.max_tavily_results,
    search_depth="advanced",
    tavily_api_key=os.getenv("TAVILY_API")
)

# Initialize OpenAI embedding model for vector operations
embedding_function = OpenAIEmbeddings(model=CFG.embedding_model)

# Load the FAISS index from disk with safety checks
try:
    db = FAISS.load_local(
        str(CFG.faiss_dir),
        embeddings=embedding_function,
        allow_dangerous_deserialization=True  # Required for loading saved indexes
    )
    # Configure retriever with top-k results
    retriever = db.as_retriever(search_kwargs={"k": 3})
except Exception as e:
    raise ValueError(f"Failed to load FAISS index: {str(e)}")


@tool
def retrieve_documents(query: str) -> str:
    """
    Retrieve relevant documents from the FAISS vector store based on the query.

    This tool searches through the local document store using vector similarity
    and returns the most relevant documents for the given query.

    Args:
        query: The search query to find relevant documents

    Returns:
        A formatted string containing the retrieved documents with metadata (if available)
    """
    try:
        # Retrieve relevant documents using the configured retriever
        documents = retriever.get_relevant_documents(query)

        if not documents:
            return "No relevant documents found for the given query."

        # Format documents for readability and include metadata
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            content = doc.page_content.strip()

            # Include metadata information if available
            if doc.metadata:
                metadata_str = " | ".join(f"{k}: {v}" for k, v in doc.metadata.items())
                formatted_docs.append(f"Document {i} ({metadata_str}):\n{content}\n")
            else:
                formatted_docs.append(f"Document {i}:\n{content}\n")

        return "\n".join(formatted_docs)

    except Exception as e:
        return f"Error retrieving documents: {str(e)}"


# Combine all available tools for the agent to use
tools = [
    search_tavily,      # Web search capability
    retrieve_documents  # Local document retrieval capability
]


def answer_question(input_state: State) -> dict:
    """Generate the final answer using available tools if needed.

    This function processes the current state and generates a response using
    the LLM with access to tools. The LLM decides whether to use tools based
    on the query requirements.

    Args:
        input_state: Current conversation state containing message history

    Returns:
        dict: Updated state with the assistant's response message
    """
    # Create system message with the main prompt
    system_message = SystemMessage(content=MultiAgentPrompts.main_prompt)

    # Bind tools to the LLM to make them available during generation
    llm_with_tools = llm.bind_tools(tools)

    # Generate response with context from system prompt and conversation history
    response = llm_with_tools.invoke([system_message] + input_state["messages"])

    return {"messages": [response]}


# Build the conversation graph
graph_builder = StateGraph(State)

# Add nodes to the graph
graph_builder.add_node("assistant", answer_question)
graph_builder.add_node("tools", ToolNode(tools))

# Set the entry point for the conversation flow
graph_builder.set_entry_point("assistant")

# Use conditional edges to determine if tools are needed
graph_builder.add_conditional_edges(
    "assistant",  # Source node
    tools_condition,  # Built-in condition function that checks for tool calls
    {
        "tools": "tools",  # If tools are needed, route to tools node
        END: END,  # If no tools needed, end the conversation
    }
)

# After using tools, go back to generate the final answer
graph_builder.add_edge("tools", "assistant")

# Compile the graph into an executable workflow
graph = graph_builder.compile()
