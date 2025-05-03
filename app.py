import json
import os

from pydantic import BaseModel

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from src.config import CFG
from src.chatbot.agent import graph, State


# Load environment variables
load_dotenv(dotenv_path=CFG.env_variable_file)


class AskRequest(BaseModel):
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
    """
    if CFG.history_dir.exists():
        with open(CFG.history_dir, "r") as f:
            chat_history = json.load(f)
        return chat_history
    else:
        return [{}]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive query from client
            query = await websocket.receive_text()
            query_text = json.loads(query)["message"]

            # Prepare the initial state for the agent
            state: State = {"messages": [HumanMessage(content=query)]}

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
