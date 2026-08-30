import pandas as pd


REQUIRED_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]


def validate_required_columns(df: pd.DataFrame) -> None:
    """Fail if the expected source columns are missing."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def transform_workload(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply the fixed Traditional cleaning/business rules.

    Returns:
        accepted_df
        rejected_df

    Business rules are added incrementally once frozen.
    """

    validate_required_columns(df)

    work = df.copy()

    # TODO:
    # 1. standardise InvoiceDate
    # 2. identify cancellations
    # 3. identify/remove exact duplicates
    # 4. apply missing-value rules
    # 5. validate Quantity
    # 6. validate Price
    # 7. calculate SalesAmount
    # 8. separate accepted/rejected records

    accepted_df = work.copy()

    rejected_df = pd.DataFrame(
        columns=list(work.columns) + ["RejectionReason"]
    )

    return accepted_df, rejected_df