import pandas as pd

from traditional.config.rules import (
    CANCELLATION_PREFIX,
    REQUIRED_COLUMNS,
)


def validate_required_columns(df: pd.DataFrame) -> None:
    """Confirm that all expected source columns exist."""

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
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Apply the Traditional pipeline's fixed transformation
    and data-quality rules.

    Returns:
        accepted_df
        rejected_df
        duplicates_df
    """

    validate_required_columns(df)

    work = df.copy()

    # Traceability within the generated workload
    work["SourceRow"] = range(1, len(work) + 1)

    # Standardise invoice date
    work["InvoiceDate"] = pd.to_datetime(
        work["InvoiceDate"],
        errors="coerce",
    )

    # Identify cancellations
    work["IsCancellation"] = (
        work["Invoice"]
        .astype("string")
        .str.startswith(
            CANCELLATION_PREFIX,
            na=False,
        )
    )

    # Quality flags that do not require rejection
    work["MissingCustomerFlag"] = (
        work["Customer ID"].isna()
    )

    work["MissingDescriptionFlag"] = (
        work["Description"].isna()
    )

    # Detect exact duplicate source records
    work["DuplicateFlag"] = work.duplicated(
        subset=REQUIRED_COLUMNS,
        keep="first",
    )

    # Convert numeric fields
    work["Quantity"] = pd.to_numeric(
        work["Quantity"],
        errors="coerce",
    )

    work["Price"] = pd.to_numeric(
        work["Price"],
        errors="coerce",
    )

    # Rejection reason starts empty
    rejection_reason = pd.Series(
        pd.NA,
        index=work.index,
        dtype="string",
    )

    # Missing Invoice
    rejection_reason = rejection_reason.mask(
        work["Invoice"].isna(),
        "Missing Invoice",
    )

    # Missing StockCode
    rejection_reason = rejection_reason.mask(
        rejection_reason.isna()
        & work["StockCode"].isna(),
        "Missing StockCode",
    )

    # Invalid or missing InvoiceDate
    rejection_reason = rejection_reason.mask(
        rejection_reason.isna()
        & work["InvoiceDate"].isna(),
        "Invalid or missing InvoiceDate",
    )

    # Invalid or missing Quantity
    rejection_reason = rejection_reason.mask(
        rejection_reason.isna()
        & work["Quantity"].isna(),
        "Invalid or missing Quantity",
    )

    # Invalid or missing Price
    rejection_reason = rejection_reason.mask(
        rejection_reason.isna()
        & work["Price"].isna(),
        "Invalid or missing Price",
    )

    # Missing Country
    rejection_reason = rejection_reason.mask(
        rejection_reason.isna()
        & work["Country"].isna(),
        "Missing Country",
    )

    # Negative quantity is only valid for cancellation records
    rejection_reason = rejection_reason.mask(
        rejection_reason.isna()
        & (work["Quantity"] < 0)
        & (~work["IsCancellation"]),
        "Negative Quantity on non-cancellation",
    )

    # Negative prices are rejected
    rejection_reason = rejection_reason.mask(
        rejection_reason.isna()
        & (work["Price"] < 0),
        "Negative Price",
    )

    work["RejectionReason"] = rejection_reason

    # Duplicate copies are handled separately
    duplicates_df = work[
        work["DuplicateFlag"]
    ].copy()

    # Rejected records are non-duplicates
    # that fail a validation/business rule
    rejected_df = work[
        work["RejectionReason"].notna()
        & ~work["DuplicateFlag"]
    ].copy()

    # Accepted records pass validation
    # and are not duplicate copies
    accepted_df = work[
        work["RejectionReason"].isna()
        & ~work["DuplicateFlag"]
    ].copy()

    # Derived sales measure
    accepted_df["SalesAmount"] = (
        accepted_df["Quantity"]
        * accepted_df["Price"]
    )

    return (
        accepted_df,
        rejected_df,
        duplicates_df,
    )