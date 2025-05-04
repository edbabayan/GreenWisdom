import json
import os

from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage

from src.config import CFG
from src.chatbot.agent import graph, State

# Load environment variables
load_dotenv(dotenv_path=CFG.env_variable_file)


class AskRequest(BaseModel):
    """Request model for the ask endpoint."""
    query: str


# FastAPI app
app = FastAPI()

# Allow CORS for frontend and WebSocket clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing, allow all origins, but restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)


@app.get("/api/history")
def get_history():
    """
    Endpoint to get the conversation history.

    Returns:
        list: List of conversation objects with 'user' and 'assistant' fields,
              or a list with empty object if no history exists.
    """
    if CFG.history_dir.exists():
        with open(CFG.history_dir, "r") as f:
            chat_history = json.load(f)
        return chat_history
    else:
        return [{}]


@app.post("/api/clear")
def delete_history():
    """
    Endpoint to delete the conversation history directory and its contents.

    Returns:
        None: Deletes the history file if it exists.
    """
    if CFG.history_dir.exists():
        os.remove(CFG.history_dir)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time conversation with streaming responses.

    Handles:
    1. Loading existing conversation history
    2. Processing new queries through the chatbot agent
    3. Streaming responses back to the client
    4. Saving updated conversation history

    Args:
        websocket: FastAPI WebSocket connection instance
    """
    await websocket.accept()
    try:
        while True:
            # Receive query from client
            query = await websocket.receive_text()
            query_text = json.loads(query)["message"]

            # Load existing conversation state from history
            state: State = {"messages": []}

            if CFG.history_dir.exists():
                with open(CFG.history_dir, "r") as f:
                    chat_history = json.load(f)

                # Reconstruct messages from history
                for conversation in chat_history:
                    state["messages"].append(HumanMessage(content=conversation["user"]))
                    state["messages"].append(AIMessage(content=conversation["assistant"]))

            # Add the new query to state
            state["messages"].append(HumanMessage(content=query_text))

            response = ""
            # Process the query through the graph (streaming)
            for event in graph.stream(state, stream_mode="messages"):
                response += event[0].content
                await websocket.send_text(event[0].content)

            if CFG.history_dir.exists():
                # Load existing conversation history
                with open(CFG.history_dir, "r") as f:
                    chat_history = json.load(f)

                new_conversation = {
                    "user": query_text,
                    "assistant": response,
                }

                chat_history.append(new_conversation)

                # Save the updated conversation history
                with open(CFG.history_dir, "w") as f:
                    json.dump(chat_history, f)
            else:
                # Save the conversation history
                chat_history = [
                    {
                        "user": query_text,
                        "assistant": response,
                    }
                ]

                with open(CFG.history_dir, "w") as f:
                    json.dump(chat_history, f)

            # Send final answer
            await websocket.send_text(event[0].content)

    except WebSocketDisconnect:
        print("Client disconnected")


@app.post("/api/ask")
def ask_question(request: AskRequest):
    """
    Endpoint for single question-answer interactions without streaming.

    Args:
        request: AskRequest object containing the user's query

    Returns:
        dict: Response containing the assistant's answer

    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        state: State = {"messages": [HumanMessage(content=request.query)]}
        response = graph.invoke(state)
        return {"answer": response['messages'][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")