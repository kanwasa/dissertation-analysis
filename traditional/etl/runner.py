from traditional.etl.extract import extract_workload
from traditional.etl.transform import transform_workload
from traditional.etl.dimensions import prepare_warehouse_data
from traditional.etl.load import load_warehouse
import argparse

def run_pipeline(workload_size: int) -> dict:
    """
    Execute the complete Traditional ETL pipeline.

    Returns pipeline accounting information so that
    development and benchmark runners can reuse it.
    """

    # Extract
    raw_df = extract_workload(workload_size)

    # Transform
    accepted_df, rejected_df, duplicates_df = (
        transform_workload(raw_df)
    )

    # Row-accounting validation
    accounted_rows = (
        len(accepted_df)
        + len(rejected_df)
        + len(duplicates_df)
    )

    if accounted_rows != len(raw_df):
        raise AssertionError(
            "Row accounting failed: "
            "accepted + rejected + duplicates "
            "does not equal input."
        )

    # Prepare warehouse datasets
    warehouse_data = prepare_warehouse_data(
        accepted_df
    )

    # Build audit information
    audit_data = {
        "workload_size": workload_size,
        "records_input": len(raw_df),
        "records_accepted": len(accepted_df),
        "records_rejected": len(rejected_df),
        "duplicates_removed": len(duplicates_df),

        "missing_customer_count": int(
            accepted_df["MissingCustomerFlag"].sum()
        ),

        "missing_description_count": int(
            accepted_df["MissingDescriptionFlag"].sum()
        ),

        "cancellation_count": int(
            accepted_df["IsCancellation"].sum()
        ),
    }

    # Load PostgreSQL
    load_warehouse(
        warehouse_data,
        audit_data,
    )

    # Return reusable pipeline metrics
    return audit_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Traditional ETL pipeline."
    )

    parser.add_argument(
        "--records",
        type=int,
        default=5_000,
        choices=[5_000, 10_000, 50_000, 100_000],
        help="Workload size to process.",
    )

    args = parser.parse_args()

    workload_size = args.records

    print(
        f"Running Traditional pipeline: "
        f"{workload_size:,} rows"
    )

    result = run_pipeline(workload_size)

    print()
    print("Pipeline complete.")
    print()
    print(f"Input rows:          {result['records_input']:,}")
    print(f"Accepted rows:       {result['records_accepted']:,}")
    print(f"Rejected records:    {result['records_rejected']:,}")
    print(f"Duplicates removed:  {result['duplicates_removed']:,}")
    print(f"Missing customers:   {result['missing_customer_count']:,}")
    print(
        f"Missing descriptions: "
        f"{result['missing_description_count']:,}"
    )
    print(f"Cancellations:       {result['cancellation_count']:,}")


if __name__ == "__main__":
    main()