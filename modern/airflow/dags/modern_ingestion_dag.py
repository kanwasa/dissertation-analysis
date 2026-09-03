import os
import subprocess

import pandas as pd
import psycopg2
from airflow.sdk import DAG, task
from pendulum import datetime


RAW_TABLE = "modern_raw.online_retail_raw"
WORKLOAD_DIR = "/opt/airflow/data/workloads"

DBT_PROJECT_DIR = "/opt/airflow/dbt/modern_analytics"
DBT_PROFILES_DIR = "/home/airflow/.dbt"


def get_connection():
    """Connect from Airflow Docker to the dissertation database."""

    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def run_dbt_command(*args):
    """Run a dbt command and fail the Airflow task if dbt fails."""

    command = [
        "dbt",
        *args,
        "--project-dir",
        DBT_PROJECT_DIR,
        "--profiles-dir",
        DBT_PROFILES_DIR,
    ]

    print(f"Running: {' '.join(command)}")

    subprocess.run(
        command,
        check=True,
    )


with DAG(
    dag_id="modern_ingestion",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["dissertation", "modern"],
) as dag:

    @task
    def reset_raw_table() -> None:
        """Reset the Modern raw landing table."""

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    TRUNCATE TABLE {RAW_TABLE};
                    """
                )

            conn.commit()


    @task
    def ingest_workload(
        workload_size: int,
    ) -> int:
        """Load the requested deterministic workload."""

        workload_size = int(workload_size)

        workload_path = (
            f"{WORKLOAD_DIR}/"
            f"workload_{workload_size}.csv"
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
                "Unexpected workload schema."
            )

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

        df = df.astype(object).where(
            pd.notna(df),
            None,
        )

        rows = list(
            df.itertuples(
                index=False,
                name=None,
            )
        )

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    f"""
                    INSERT INTO {RAW_TABLE} (
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

    @task
    def validate_raw_count(
        expected_count: int,
    ) -> None:
        """Verify that PostgreSQL contains the expected workload."""

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {RAW_TABLE};
                    """
                )

                actual_count = cur.fetchone()[0]

        if actual_count != expected_count:
            raise ValueError(
                f"Raw row-count validation failed: "
                f"expected {expected_count:,}, "
                f"found {actual_count:,}."
            )

        print(
            f"Raw ingestion validated: "
            f"{actual_count:,} rows."
        )


    @task
    def dbt_staging() -> None:
        run_dbt_command(
            "run",
            "--select",
            "staging",
        )


    @task
    def dbt_intermediate() -> None:
        run_dbt_command(
            "run",
            "--select",
            "intermediate",
        )


    @task
    def dbt_marts() -> None:
        run_dbt_command(
            "run",
            "--select",
            "marts",
        )


    @task
    def dbt_analytics() -> None:
        run_dbt_command(
            "run",
            "--select",
            "analytics",
        )


    @task
    def dbt_tests() -> None:
        run_dbt_command(
            "test",
        )

    reset = reset_raw_table()

    loaded_count = ingest_workload(
        workload_size="{{ dag_run.conf.get('workload_size',5000) }}"
    )

    validated = validate_raw_count(
        loaded_count
    )

    staging = dbt_staging()
    intermediate = dbt_intermediate()
    marts = dbt_marts()
    analytics = dbt_analytics()
    tests = dbt_tests()
    (
        reset
        >> loaded_count
        >> validated
        >> staging
        >> intermediate
        >> marts
        >> analytics
        >> tests
    )