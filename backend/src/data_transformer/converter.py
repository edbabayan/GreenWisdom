from pathlib import Path

import pandas as pd
from loguru import logger
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def create_faiss_index_from_csv(csv_dir: Path, faiss_dir: Path):
    """
    Loads a CSV file, generates OpenAI embeddings, and stores them in a FAISS index.

    Args:
        csv_dir (Path): Path to the input CSV file.
        faiss_dir (Path): Directory where the FAISS index will be saved.
    """
    # Read the data from CSV
    data = pd.read_csv(csv_dir)

    # Initialize OpenAI embeddings with the configured model
    embedding_function = OpenAIEmbeddings(model=CFG.embedding_model)

    # Extract texts from the 'context' column
    texts = data['context'].tolist()

    logger.info("Creating FAISS vector store...")

    # Create and save FAISS vector store
    db = FAISS.from_texts(texts, embedding=embedding_function)
    db.save_local(str(faiss_dir))

    logger.success(f"FAISS index saved to {faiss_dir}")


if __name__ == '__main__':
    from backend.src.config import CFG

    # Load environment variables
    load_dotenv(dotenv_path=CFG.env_variable_file)

    # Create FAISS index
    create_faiss_index_from_csv(CFG.csv_dir, CFG.faiss_dir)