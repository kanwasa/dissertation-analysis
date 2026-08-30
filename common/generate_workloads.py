from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
WORKLOAD_DIR = PROJECT_ROOT / "data" / "workloads"

SHEETS = [
    "Year 2009-2010",
    "Year 2010-2011",
]

WORKLOAD_SIZES = [
    5_000,
    10_000,
    50_000,
    100_000,
]

RANDOM_SEED = 42


def load_source_data() -> pd.DataFrame:
    """Load both source sheets without applying ETL cleaning rules."""

    frames = []

    for sheet_name in SHEETS:
        df = pd.read_excel(
            RAW_FILE,
            sheet_name=sheet_name,
            engine="openpyxl",
        )

        frames.append(df)

    combined = pd.concat(
        frames,
        ignore_index=True,
    )

    return combined


def create_deterministic_order(df: pd.DataFrame) -> pd.DataFrame:
    """
    Shuffle the combined source once using a fixed seed.

    The same deterministic ordering is then used to create all
    nested workloads.
    """

    shuffled = df.sample(
        frac=1,
        random_state=RANDOM_SEED,
    ).reset_index(drop=True)

    return shuffled


def save_workloads(df: pd.DataFrame) -> None:
    """Create nested workload CSV files from the deterministic ordering."""

    WORKLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for size in WORKLOAD_SIZES:

        if size > len(df):
            raise ValueError(
                f"Requested workload of {size:,} rows, "
                f"but source only contains {len(df):,} rows."
            )

        workload = df.iloc[:size].copy()

        output_path = (
            WORKLOAD_DIR
            / f"workload_{size}.csv"
        )

        workload.to_csv(
            output_path,
            index=False,
        )

        print(
            f"Created {output_path.name}: "
            f"{len(workload):,} rows"
        )


def main() -> None:

    print("Loading Online Retail II source data...")

    source_df = load_source_data()

    print(
        f"Combined source rows: "
        f"{len(source_df):,}"
    )

    print("Creating deterministic ordering...")

    ordered_df = create_deterministic_order(
        source_df
    )

    print("Generating nested workloads...")

    save_workloads(
        ordered_df
    )

    print("Workload generation complete.")


if __name__ == "__main__":
    main()