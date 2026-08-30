from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKLOAD_DIR = PROJECT_ROOT / "data" / "workloads"


def extract_workload(workload_size: int) -> pd.DataFrame:
    """Load one deterministic workload CSV."""

    workload_path = (
        WORKLOAD_DIR
        / f"workload_{workload_size}.csv"
    )

    if not workload_path.exists():
        raise FileNotFoundError(
            f"Workload file not found: {workload_path}"
        )

    df = pd.read_csv(workload_path)

    return df