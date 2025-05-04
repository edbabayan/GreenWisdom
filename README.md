# GreenWisdom

This repository provides intelligent answers to a wide range of questions about the renewable energy industry. It leverages a curated CSV file containing 30 core topics as a structured knowledge base and supplements responses with real-time online search to ensure answers are accurate, up-to-date, and comprehensive.

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
    - Create a `.env` file in the root directory of the project.
    - Add your OpenAI API key and TavilyAPI key to the `.env` file:
      ```plaintext
      OPENAI_API_KEY=your_openai_api_key
      TAVILY_API=your_serpapi_api_key
      ```
