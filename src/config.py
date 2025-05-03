from pathlib import Path


class CFG:
    root = Path(__file__).parent.parent

    env_variable_file = root / '.env'
    data_dir = root / 'data'
    csv_dir = data_dir / 'renewable_energy_topics.csv'
    faiss_dir = data_dir / 'faiss_index'
    history_dir = root / 'history.json'

    embedding_model = "text-embedding-3-large"
    llm_model = "gpt-4o-mini"