# GreenWisdom

This repository provides intelligent answers to a wide range of questions about the renewable energy industry. It leverages a curated CSV file containing 30 core topics as a structured knowledge base and supplements responses with real-time online search to ensure answers are accurate, up-to-date, and comprehensive.

## Features
- **Structured Knowledge Base**: The CSV file contains 30 core topics related to the renewable energy industry, providing a solid foundation for answering questions.
- **Real-time Online Search**: The system can perform online searches to supplement the knowledge base, ensuring that answers are accurate and up-to-date.
- **Intelligent Responses**: The system is designed to provide intelligent and contextually relevant answers to a wide range of questions.
- **User-Friendly Interface**: The system is designed to be user-friendly, making it easy for users to ask questions and receive answers.

## Getting Started
To get started with the GreenWisdom project, follow these steps:
1. Clone the repository to your local machine.
    ```bash
    git clone https://github.com/edbabayan/GreenWisdom.git
   ```
2. Navigate to the project directory.
    ```bash
    cd GreenWisdom
    ```
3. Set up environment variables:
    - Create a `.env` file in the backend directory of the project.
    - Add your OpenAI API key and TavilyAPI key to the `.env` file:
      ```plaintext
      OPENAI_API_KEY=your_openai_api_key
      TAVILY_API=your_serpapi_api_key
      ```
4. Run the docker-compose command to start the application.
    ```bash
    docker-compose up
    ```
5. Access the application in your web browser at `http://localhost:3000`.
6. Ask questions about the renewable energy industry and receive intelligent answers.
7. Explore the CSV(backend/data/renewable_energy_topics.csv) file to understand the core topics covered in the knowledge base.

## Technologies Used
- **Python**: The primary programming language used for the backend.
- **Flask**: A lightweight WSGI web application framework for Python.
- **Docker**: Used for containerization, making it easy to deploy the application in different environments.
- **OpenAI API**: Used for generating intelligent responses to user queries.
- **FAISS**: A library for efficient similarity search and clustering of dense vectors, used for searching the knowledge base.
- **REACT**: A JavaScript library for building user interfaces, used for the frontend.

### To change from streaming to non-streaming, change the following line in the `frontend/app.jsx` file:
- **Streaming (default)**: Uses sendQuestion for real-time streaming responses.
- **HTTP POST**: Uses sendQuestionViaHTTP to send a standard POST request to the API.

To use HTTP mode, pass sendQuestionViaHTTP as the onSend prop to the InputBar component. Otherwise, sendQuestion will be used by default for streaming