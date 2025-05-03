from typing import List, Tuple

from loguru import logger
from tavily import TavilyClient
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings

from src.config import CFG


def search_context(
    query: str,
    top_k: int = 3,
    threshold: float = 0.5
) -> List[Tuple[str, float]]:
    """
    Search the FAISS index using L2 distance and return results filtered by cosine similarity.

    Args:
        query (str): The search query.
        top_k (int): Number of top results to retrieve.
        threshold (float): Minimum cosine similarity to include in results.

    Returns:
        List[Tuple[str, float]]: A list of (matched_text, cosine_similarity) tuples.
    """
    # Initialize OpenAI embedding model
    embedding_function = OpenAIEmbeddings(model=CFG.embedding_model)

    # Load the FAISS index from disk
    db = FAISS.load_local(
        str(CFG.faiss_dir),
        embeddings=embedding_function,
        allow_dangerous_deserialization=True
    )

    # Perform similarity search and retrieve (Document, L2_distance) pairs
    results_with_scores = db.similarity_search_with_score(query, k=top_k)

    # Convert L2 distance to cosine similarity: cos_sim = 1 - (distance / 2)
    filtered_results = [
        (doc.page_content, 1 - score / 2)
        for doc, score in results_with_scores
        if (1 - score / 2) >= threshold
    ]

    logger.info(f"Retrieved {len(filtered_results)} results above threshold {threshold}")

    return filtered_results


if __name__ == '__main__':
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv(dotenv_path=CFG.env_variable_file)

    # Example query
    question = "How does photosynthesis work in plants?"

    # Run the search
    results = search_context(
        query=question,
        top_k=3,
        threshold=0.6
    )

    # Display the results
    for i, (text, score) in enumerate(results, start=1):
        print(f"\nResult {i}:")
        print(f"Cosine Similarity: {score:.4f}")
        print(f"Content: {text}")


def web_search_tavily(query: str, max_results: int = 3) -> List[str]:
    """
    Perform a web search using the Tavily API and return a list of snippets.

    Args:
        query (str): The search query.
        max_results (int): Number of top results to return.

    Returns:
        List[str]: A list of text snippets from the web.
    """
    try:
        client = TavilyClient()

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )

        snippets = [res["content"] for res in response.get("results", [])[:max_results]]

        logger.info(f"Retrieved {len(snippets)} web search results from Tavily for query: '{query}'")

        return snippets

    except Exception as e:
        logger.error(f"Error during Tavily web search: {e}")
        return []
