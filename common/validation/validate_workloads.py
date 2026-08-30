from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

WORKLOAD_DIR = PROJECT_ROOT / "data" / "workloads"

WORKLOAD_SIZES = [
    5_000,
    10_000,
    50_000,
    100_000,
]

EXPECTED_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]


def load_workloads() -> dict[int, pd.DataFrame]:
    """Load all generated workload CSV files."""

    workloads = {}

    for size in WORKLOAD_SIZES:
        path = WORKLOAD_DIR / f"workload_{size}.csv"

        if not path.exists():
            raise FileNotFoundError(
                f"Missing workload file: {path}"
            )

        workloads[size] = pd.read_csv(path)

    return workloads


def validate_row_counts(
    workloads: dict[int, pd.DataFrame],
) -> None:
    """Confirm each workload contains exactly the intended row count."""

    for size, df in workloads.items():
        actual = len(df)

        if actual != size:
            raise AssertionError(
                f"workload_{size}.csv has {actual:,} rows; "
                f"expected {size:,}."
            )

        print(
            f"[PASS] workload_{size}.csv contains "
            f"{actual:,} rows."
        )


def validate_columns(
    workloads: dict[int, pd.DataFrame],
) -> None:
    """Confirm all workload files retain the expected source columns."""

    for size, df in workloads.items():
        actual_columns = list(df.columns)

        if actual_columns != EXPECTED_COLUMNS:
            raise AssertionError(
                f"Unexpected columns in workload_{size}.csv\n"
                f"Expected: {EXPECTED_COLUMNS}\n"
                f"Actual:   {actual_columns}"
            )

        print(
            f"[PASS] workload_{size}.csv has the expected columns."
        )


def validate_nesting(
    workloads: dict[int, pd.DataFrame],
) -> None:
    """
    Confirm that each smaller workload is exactly the prefix
    of the next larger workload.
    """

    comparisons = [
        (5_000, 10_000),
        (10_000, 50_000),
        (50_000, 100_000),
    ]

    for smaller_size, larger_size in comparisons:

        smaller = workloads[smaller_size].reset_index(drop=True)

        larger_prefix = (
            workloads[larger_size]
            .iloc[:smaller_size]
            .reset_index(drop=True)
        )

        if not smaller.equals(larger_prefix):
            raise AssertionError(
                f"workload_{smaller_size}.csv is not nested "
                f"inside workload_{larger_size}.csv."
            )

        print(
            f"[PASS] {smaller_size:,} is nested inside "
            f"{larger_size:,}."
        )


def profile_workload(
    size: int,
    df: pd.DataFrame,
) -> None:
    """Print a non-destructive data-quality profile."""

    invoice_text = df["Invoice"].astype("string")

    cancellations = (
        invoice_text
        .str.startswith("C", na=False)
        .sum()
    )

    exact_duplicates = df.duplicated().sum()

    negative_quantity = (
        pd.to_numeric(
            df["Quantity"],
            errors="coerce",
        ) < 0
    ).sum()

    zero_or_negative_price = (
        pd.to_numeric(
            df["Price"],
            errors="coerce",
        ) <= 0
    ).sum()

    unique_countries = df["Country"].nunique(
        dropna=True
    )

    unique_customers = df["Customer ID"].nunique(
        dropna=True
    )

    parsed_dates = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce",
    )

    print()
    print(f"--- Workload {size:,} Profile ---")
    print(f"Rows: {len(df):,}")
    print(f"Exact duplicates: {exact_duplicates:,}")
    print(f"Cancellations: {cancellations:,}")
    print(f"Negative quantities: {negative_quantity:,}")
    print(
        f"Zero/negative prices: "
        f"{zero_or_negative_price:,}"
    )
    print(f"Unique countries: {unique_countries:,}")
    print(f"Unique customers: {unique_customers:,}")
    print(
        f"Unparseable dates: "
        f"{parsed_dates.isna().sum():,}"
    )
    print(
        f"Date range: "
        f"{parsed_dates.min()} "
        f"to {parsed_dates.max()}"
    )

    print("Missing values by column:")

    missing = df.isna().sum()

    for column, count in missing.items():
        print(
            f"  {column}: {count:,}"
        )


def main() -> None:

    print("Loading generated workloads...")

    workloads = load_workloads()

    print("\nValidating workload structure...")

    validate_row_counts(workloads)
    validate_columns(workloads)
    validate_nesting(workloads)

    print("\nProfiling natural data-quality characteristics...")

    for size in WORKLOAD_SIZES:
        profile_workload(
            size,
            workloads[size],
        )

    print("\nAll workload validation checks passed.")


if __name__ == "__main__":
    main()