from pydantic import BaseModel

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import CFG
from src.chatbot.agent import graph, State  # Adjust path to your agent module

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive query from client
            query = await websocket.receive_text()

            # Prepare the initial state for the agent
            state: State = {"messages": [HumanMessage(content=query)]}

            # Process the query through the graph (streaming)
            for event in graph.stream(state, stream_mode="messages"):
                await websocket.send_text(event[0].content)

            # Send final answer
            await websocket.send_text(event[0].content)

    except WebSocketDisconnect:
        print("Client disconnected")
