from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.config import CFG
from src.chatbot.agent import ChatAgent  # Adjust path to your agent module


# Load environment variables
load_dotenv(dotenv_path=CFG.env_variable_file)

# FastAPI app setup
app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the chat agent
chat_agent = ChatAgent()

@app.get("/")
def root():
    return {"message": "Welcome to the ChatBot API!"}


@app.get("/stream_answer")
def stream_response(query: str):
    """
    Streaming endpoint that sends data as Server-Sent Events (SSE).
    The `query` parameter is passed to the ChatAgent for processing.
    """

    return StreamingResponse(chat_agent.stream(query), media_type="text/event-stream")

@app.post("/ask")
def ask_question(query: str):
    """
    Regular endpoint that gets a complete response from the ChatAgent.
    """
    response = chat_agent.ask(query)
    return response
