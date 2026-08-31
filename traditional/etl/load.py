from pathlib import Path
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def get_connection():
    """Create a PostgreSQL connection from .env settings."""

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def load_customer_dimension(
    conn,
    dim_customer: pd.DataFrame,
) -> None:

    with conn.cursor() as cur:
        for row in dim_customer.itertuples(index=False):

            cur.execute(
                """
                INSERT INTO traditional_dw.dim_customer (
                    customer_id
                )
                VALUES (%s)
                ON CONFLICT (customer_id)
                DO NOTHING;
                """,
                (
                    row.customer_id,
                ),
            )


def load_product_dimension(
    conn,
    dim_product: pd.DataFrame,
) -> None:

    with conn.cursor() as cur:
        for row in dim_product.itertuples(index=False):

            cur.execute(
                """
                INSERT INTO traditional_dw.dim_product (
                    stock_code,
                    description
                )
                VALUES (%s, %s)
                ON CONFLICT (stock_code)
                DO NOTHING;
                """,
                (
                    row.stock_code,
                    row.description,
                ),
            )


def load_date_dimension(
    conn,
    dim_date: pd.DataFrame,
) -> None:

    with conn.cursor() as cur:
        for row in dim_date.itertuples(index=False):

            cur.execute(
                """
                INSERT INTO traditional_dw.dim_date (
                    full_timestamp,
                    calendar_date,
                    year,
                    month,
                    day,
                    hour
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (full_timestamp)
                DO NOTHING;
                """,
                (
                    row.full_timestamp,
                    row.calendar_date,
                    row.year,
                    row.month,
                    row.day,
                    row.hour,
                ),
            )


def load_country_dimension(
    conn,
    dim_country: pd.DataFrame,
) -> None:

    with conn.cursor() as cur:
        for row in dim_country.itertuples(index=False):

            cur.execute(
                """
                INSERT INTO traditional_dw.dim_country (
                    country_name
                )
                VALUES (%s)
                ON CONFLICT (country_name)
                DO NOTHING;
                """,
                (
                    row.country_name,
                ),
            )


def fetch_dimension_keys(conn) -> dict[str, pd.DataFrame]:
    """Retrieve business identifiers and surrogate keys."""

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                customer_key,
                customer_id
            FROM traditional_dw.dim_customer;
            """
        )
        customer_rows = cur.fetchall()

        cur.execute(
            """
            SELECT
                product_key,
                stock_code
            FROM traditional_dw.dim_product;
            """
        )
        product_rows = cur.fetchall()

        cur.execute(
            """
            SELECT
                date_key,
                full_timestamp
            FROM traditional_dw.dim_date;
            """
        )
        date_rows = cur.fetchall()

        cur.execute(
            """
            SELECT
                country_key,
                country_name
            FROM traditional_dw.dim_country;
            """
        )
        country_rows = cur.fetchall()

    return {
        "dim_customer": pd.DataFrame(
            customer_rows,
            columns=["customer_key", "customer_id"],
        ),
        "dim_product": pd.DataFrame(
            product_rows,
            columns=["product_key", "stock_code"],
        ),
        "dim_date": pd.DataFrame(
            date_rows,
            columns=["date_key", "full_timestamp"],
        ),
        "dim_country": pd.DataFrame(
            country_rows,
            columns=["country_key", "country_name"],
        ),
    }


def build_fact_sales(
    fact_source: pd.DataFrame,
    keys: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Attach surrogate dimension keys to fact records."""

    fact = fact_source.copy()

    fact = fact.merge(
        keys["dim_customer"],
        how="left",
        on="customer_id",
    )

    fact = fact.merge(
        keys["dim_product"],
        how="left",
        on="stock_code",
    )

    fact = fact.merge(
        keys["dim_date"],
        how="left",
        on="full_timestamp",
    )

    fact = fact.merge(
        keys["dim_country"],
        how="left",
        on="country_name",
    )

    return fact


def load_fact_sales(
    conn,
    fact_sales: pd.DataFrame,
) -> None:

    with conn.cursor() as cur:

        for row in fact_sales.itertuples(index=False):

            customer_key = (
                None
                if pd.isna(row.customer_key)
                else int(row.customer_key)
            )

            cur.execute(
                """
                INSERT INTO traditional_dw.fact_sales (
                    invoice_no,
                    customer_key,
                    product_key,
                    date_key,
                    country_key,
                    quantity,
                    unit_price,
                    sales_amount,
                    is_cancellation,
                    missing_customer_flag,
                    missing_description_flag,
                    source_row
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                );
                """,
                (
                    row.invoice_no,
                    customer_key,
                    int(row.product_key),
                    int(row.date_key),
                    int(row.country_key),
                    row.quantity,
                    row.unit_price,
                    row.sales_amount,
                    bool(row.is_cancellation),
                    bool(row.missing_customer_flag),
                    bool(row.missing_description_flag),
                    int(row.source_row),
                ),
            )

def load_run_audit(
    conn,
    workload_size: int,
    records_input: int,
    records_accepted: int,
    records_rejected: int,
    duplicates_removed: int,
    missing_customer_count: int,
    missing_description_count: int,
    cancellation_count: int,
) -> None:
    """Persist one Traditional pipeline quality/accounting record."""

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO traditional_dw.pipeline_run_audit (
                workload_size,
                records_input,
                records_accepted,
                records_rejected,
                duplicates_removed,
                missing_customer_count,
                missing_description_count,
                cancellation_count
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                workload_size,
                records_input,
                records_accepted,
                records_rejected,
                duplicates_removed,
                missing_customer_count,
                missing_description_count,
                cancellation_count,
            ),
        )

def load_warehouse(
    warehouse_data: dict[str, pd.DataFrame],
    audit_data: dict,
) -> None:
    """Load all prepared Traditional warehouse datasets."""

    with get_connection() as conn:

        load_customer_dimension(
            conn,
            warehouse_data["dim_customer"],
        )

        load_product_dimension(
            conn,
            warehouse_data["dim_product"],
        )

        load_date_dimension(
            conn,
            warehouse_data["dim_date"],
        )

        load_country_dimension(
            conn,
            warehouse_data["dim_country"],
        )

        keys = fetch_dimension_keys(conn)

        fact_sales = build_fact_sales(
            warehouse_data["fact_source"],
            keys,
        )

        load_fact_sales(
            conn,
            fact_sales,
        )

        load_run_audit(
            conn,
            workload_size=audit_data["workload_size"],
            records_input=audit_data["records_input"],
            records_accepted=audit_data["records_accepted"],
            records_rejected=audit_data["records_rejected"],
            duplicates_removed=audit_data["duplicates_removed"],
            missing_customer_count=audit_data["missing_customer_count"],
            missing_description_count=audit_data[
                "missing_description_count"
            ],
            cancellation_count=audit_data["cancellation_count"],
        )

        conn.commit()


