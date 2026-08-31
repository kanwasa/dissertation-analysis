from traditional.etl.extract import extract_workload
from traditional.etl.transform import transform_workload


def main() -> None:
    workload_size = 10_000

    print(f"Loading workload: {workload_size:,} rows")

    raw_df = extract_workload(workload_size)

    accepted_df, rejected_df = transform_workload(raw_df)

    duplicate_mask = (
        rejected_df["RejectionReason"] == "Exact Duplicate"
    )

    duplicates_removed = rejected_df[duplicate_mask]
    invalid_rejected = rejected_df[~duplicate_mask]

    print()
    print(f"Input rows:             {len(raw_df):,}")
    print(f"Accepted rows:          {len(accepted_df):,}")
    print(f"Rejected records:       {len(invalid_rejected):,}")
    print(f"Duplicates removed:     {len(duplicates_removed):,}")

    accounted_rows = (
        len(accepted_df)
        + len(invalid_rejected)
        + len(duplicates_removed)
    )

    print(f"Accounted rows:         {accounted_rows:,}")

    if accounted_rows != len(raw_df):
        raise AssertionError(
            "Row accounting failed: "
            "input does not equal accepted + rejected + duplicates."
        )

    print()
    print("Rejection reasons:")
    print(
        invalid_rejected["RejectionReason"]
        .value_counts(dropna=False)
    )

    print()
    print("Quality flags in accepted records:")
    print(
        "Missing Customer ID:",
        accepted_df["MissingCustomerFlag"].sum(),
    )
    print(
        "Missing Description:",
        accepted_df["MissingDescriptionFlag"].sum(),
    )
    print(
        "Cancellations:",
        accepted_df["IsCancellation"].sum(),
    )


if __name__ == "__main__":
    main()