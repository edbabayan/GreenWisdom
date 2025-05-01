from pathlib import Path


class CFG:
    root = Path(__file__).parent.parent

    data_dir = root / 'data'
    csv_dir = data_dir / 'renewable_energy_topics.csv'
