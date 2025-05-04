# Getting started with the Renewable Energy Q&A Bot

## Overview
This chatbot uses LangGraph and LangChain to build an intelligent agent capable of answering questions about renewable energy. The system utilizes:
- **LangGraph**: For building the conversation flow and agent orchestration
- **LangChain**: For managing the interaction between different components
- **FAISS Vector Database**: For storing and retrieving document embeddings
- **Tavily Search**: For finding relevant content from the web when needed

## Environment Setup

1. **Create and activate a Python virtual environment**:

   **For Linux/macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
    ```
   **For Windows:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
   ```
2. **Install the required packages**:
   ```bash
    pip install -r requirements.txt
    ```
3. **Set up environment variables**:
    - Create a `.env` file in the backend directory of the project.
    - Add your OpenAI API key and TavilyAPI key to the `.env` file:
      ```plaintext
      OPENAI_API_KEY=your_openai_api_key
      TAVILY_API=your_serpapi_api_key
      ```


## Testing
To run tests with pytest, first set the PYTHONPATH and then run pytest:

```bash
export PYTHONPATH=/Users/eduard_babayan/Documents/GreenWisdom/backend:$PYTHONPATH
pytest tests/
```