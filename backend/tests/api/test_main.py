import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from langchain_core.messages import HumanMessage, AIMessage

# Import your FastAPI app from the correct location
from app import app  # Since tests are in backend/tests, we can import directly from app.py


class TestAskEndpoint:
    """Integration tests for the /api/ask endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_ask_endpoint_success(self, client):
        """Test successful question-answer interaction."""
        # Mock the graph.invoke response
        mock_response = {
            "messages": [
                HumanMessage(content="What is the capital of France?"),
                AIMessage(content="The capital of France is Paris.")
            ]
        }

        with patch('app.graph.invoke') as mock_invoke:  # Update the patch path
            mock_invoke.return_value = mock_response

            # Make a POST request to the endpoint
            response = client.post("/api/ask", json={"query": "What is the capital of France?"})

            # Assert the response status code
            assert response.status_code == 200

            # Assert the response structure
            json_response = response.json()
            assert "answer" in json_response
            assert json_response["answer"] == "The capital of France is Paris."

            # Verify the graph was called with the correct state
            mock_invoke.assert_called_once()
            called_state = mock_invoke.call_args[0][0]
            assert "messages" in called_state
            assert len(called_state["messages"]) == 1
            assert isinstance(called_state["messages"][0], HumanMessage)
            assert called_state["messages"][0].content == "What is the capital of France?"

    def test_ask_endpoint_empty_query(self, client):
        """Test behavior with empty query."""
        mock_response = {
            "messages": [
                HumanMessage(content=""),
                AIMessage(content="Please provide a question.")
            ]
        }

        with patch('app.graph.invoke') as mock_invoke:
            mock_invoke.return_value = mock_response

            response = client.post("/api/ask", json={"query": ""})

            assert response.status_code == 200
            json_response = response.json()
            assert "answer" in json_response
            assert json_response["answer"] == "Please provide a question."

    def test_ask_endpoint_invalid_json(self, client):
        """Test behavior with invalid JSON payload."""
        response = client.post("/api/ask", json={"wrong_key": "test"})

        # FastAPI returns 422 for validation errors
        assert response.status_code == 422

    def test_ask_endpoint_missing_payload(self, client):
        """Test behavior when no payload is sent."""
        response = client.post("/api/ask")

        # FastAPI returns 422 for missing required fields
        assert response.status_code == 422

    def test_ask_endpoint_graph_error(self, client):
        """Test error handling when graph.invoke fails."""
        with patch('app.graph.invoke') as mock_invoke:
            mock_invoke.side_effect = Exception("Graph processing error")

            # The current implementation doesn't handle exceptions,
            # so this will raise a 500 error
            response = client.post("/api/ask", json={"query": "Test question"})

            assert response.status_code == 500