import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document

# Import the function to test
from src.chatbot.agent import retrieve_documents


class TestRetrieveDocuments:
    """Test cases for the retrieve_documents function."""

    def test_retrieve_documents_success(self):
        """Test successful document retrieval with sample query."""
        # Mock the retriever and its response
        mock_doc1 = Document(
            page_content="This is a sample document about machine learning.",
            metadata={"source": "file1.pdf", "page": 1}
        )
        mock_doc2 = Document(
            page_content="Another document discussing AI technologies.",
            metadata={"source": "file2.pdf", "page": 5}
        )

        # Create a mock retriever that returns our mock documents
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.return_value = [mock_doc1, mock_doc2]

        # Patch the retriever in the actual module
        with patch('src.chatbot.agent.retriever', mock_retriever):
            result = retrieve_documents.invoke("machine learning")  # Use invoke instead of direct call

            # Verify the retriever was called with the correct query
            mock_retriever.get_relevant_documents.assert_called_once_with("machine learning")

            # Check the returned format
            assert "Document 1" in result
            assert "Document 2" in result
            assert "machine learning" in result
            assert "AI technologies" in result
            assert "source: file1.pdf" in result
            assert "page: 1" in result

    def test_retrieve_documents_no_results(self):
        """Test behavior when no documents are found."""
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.return_value = []

        with patch('src.chatbot.agent.retriever', mock_retriever):
            result = retrieve_documents.invoke("nonexistent topic")
            assert result == "No relevant documents found for the given query."

    def test_retrieve_documents_with_error(self):
        """Test error handling when retriever fails."""
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.side_effect = Exception("Retrieval error")

        with patch('src.chatbot.agent.retriever', mock_retriever):
            result = retrieve_documents.invoke("test query")
            assert "Error retrieving documents:" in result
            assert "Retrieval error" in result

    def test_retrieve_documents_without_metadata(self):
        """Test document formatting when metadata is missing."""
        # Use an empty dict instead of None for metadata
        mock_doc = Document(
            page_content="Document without metadata",
            metadata={}  # Empty dict instead of None
        )

        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.return_value = [mock_doc]

        with patch('src.chatbot.agent.retriever', mock_retriever):
            result = retrieve_documents.invoke("test query")
            assert "Document 1:" in result
            assert "Document without metadata" in result
            # Ensure no metadata section is present
            assert "|" not in result