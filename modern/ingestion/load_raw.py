from pathlib import Path
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT_ENV = PROJECT_ROOT / ".env"

load_dotenv(ROOT_ENV)


def get_connection():
    """
    Connect to the dissertation PostgreSQL database.

    NOTE:
    This works when executed from Windows/local Python.
    Airflow containers will later use host.docker.internal
    instead of localhost.
    """

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def ingest_workload(workload_size: int) -> int:
    """
    Load one deterministic workload into the Modern raw layer.

    No cleaning or business transformations are applied here.
    """

    workload_path = (
        PROJECT_ROOT
        / "data"
        / "workloads"
        / f"workload_{workload_size}.csv"
    )

    if not workload_path.exists():
        raise FileNotFoundError(
            f"Workload file not found: {workload_path}"
        )

    df = pd.read_csv(
        workload_path,
        dtype="string",
    )

    expected_columns = [
        "Invoice",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "Price",
        "Customer ID",
        "Country",
    ]

    if list(df.columns) != expected_columns:
        raise ValueError(
            "Unexpected workload schema.\n"
            f"Expected: {expected_columns}\n"
            f"Actual:   {list(df.columns)}"
        )

    # Rename columns for clean Python/PostgreSQL handling
    df.columns = [
        "invoice",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "price",
        "customer_id",
        "country",
    ]

        # Convert pandas missing values to Python None
    # so psycopg inserts them as SQL NULL.
    df = df.astype(object).where(
        pd.notna(df),
        None,
    )

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Raw layer is reset for each workload run
            cur.execute(
                """
                TRUNCATE TABLE
                    modern_raw.online_retail_raw;
                """
            )

            rows = [
                (
                    row.invoice,
                    row.stock_code,
                    row.description,
                    row.quantity,
                    row.invoice_date,
                    row.price,
                    row.customer_id,
                    row.country,
                )
                for row in df.itertuples(index=False)
            ]
            cur.executemany(
                """
                INSERT INTO modern_raw.online_retail_raw (
                    invoice,
                    stock_code,
                    description,
                    quantity,
                    invoice_date,
                    price,
                    customer_id,
                    country
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                );
                """,
                rows,
            )

        conn.commit()

    return len(df)


if __name__ == "__main__":
    workload_size = 5_000

    rows_loaded = ingest_workload(workload_size)

    print(
        f"Loaded {rows_loaded:,} rows "
        "into modern_raw.online_retail_raw."
    )