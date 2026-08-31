import pandas as pd


def prepare_customer_dimension(
    accepted_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare unique non-null customer IDs.
    Rows with missing Customer ID remain valid fact rows later,
    but do not create a customer dimension record.
    """

    dim_customer = (
        accepted_df[["Customer ID"]]
        .dropna()
        .drop_duplicates()
        .rename(
            columns={
                "Customer ID": "customer_id",
            }
        )
        .reset_index(drop=True)
    )

    return dim_customer


def prepare_product_dimension(
    accepted_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare unique products using StockCode as the
    business identifier.
    """

    dim_product = (
        accepted_df[
            [
                "StockCode",
                "Description",
            ]
        ]
        .drop_duplicates(
            subset=["StockCode"],
            keep="first",
        )
        .rename(
            columns={
                "StockCode": "stock_code",
                "Description": "description",
            }
        )
        .reset_index(drop=True)
    )

    return dim_product


def prepare_date_dimension(
    accepted_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare one row per distinct invoice timestamp.
    """

    timestamps = (
        accepted_df[["InvoiceDate"]]
        .drop_duplicates()
        .rename(
            columns={
                "InvoiceDate": "full_timestamp",
            }
        )
        .reset_index(drop=True)
    )

    timestamps["calendar_date"] = (
        timestamps["full_timestamp"].dt.date
    )

    timestamps["year"] = (
        timestamps["full_timestamp"].dt.year
    )

    timestamps["month"] = (
        timestamps["full_timestamp"].dt.month
    )

    timestamps["day"] = (
        timestamps["full_timestamp"].dt.day
    )

    timestamps["hour"] = (
        timestamps["full_timestamp"].dt.hour
    )

    return timestamps


def prepare_country_dimension(
    accepted_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare one row per country.
    """

    dim_country = (
        accepted_df[["Country"]]
        .drop_duplicates()
        .rename(
            columns={
                "Country": "country_name",
            }
        )
        .reset_index(drop=True)
    )

    return dim_country


def prepare_fact_source(
    accepted_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the source fields needed to construct fact_sales.

    Surrogate dimension keys are added later after the
    dimensions have been loaded into PostgreSQL.
    """

    fact_source = (
        accepted_df[
            [
                "Invoice",
                "Customer ID",
                "StockCode",
                "InvoiceDate",
                "Country",
                "Quantity",
                "Price",
                "SalesAmount",
                "IsCancellation",
                "MissingCustomerFlag",
                "MissingDescriptionFlag",
                "SourceRow",
            ]
        ]
        .rename(
            columns={
                "Invoice": "invoice_no",
                "Customer ID": "customer_id",
                "StockCode": "stock_code",
                "InvoiceDate": "full_timestamp",
                "Country": "country_name",
                "Quantity": "quantity",
                "Price": "unit_price",
                "SalesAmount": "sales_amount",
                "IsCancellation": "is_cancellation",
                "MissingCustomerFlag": "missing_customer_flag",
                "MissingDescriptionFlag": "missing_description_flag",
                "SourceRow": "source_row",
            }
        )
        .reset_index(drop=True)
    )

    return fact_source


def prepare_warehouse_data(
    accepted_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Prepare all Traditional warehouse datasets.
    """

    return {
        "dim_customer": prepare_customer_dimension(
            accepted_df
        ),
        "dim_product": prepare_product_dimension(
            accepted_df
        ),
        "dim_date": prepare_date_dimension(
            accepted_df
        ),
        "dim_country": prepare_country_dimension(
            accepted_df
        ),
        "fact_source": prepare_fact_source(
            accepted_df
        ),
    }