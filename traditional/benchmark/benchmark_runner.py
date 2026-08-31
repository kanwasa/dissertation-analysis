import csv
import os
import time
from datetime import datetime
from pathlib import Path

import psutil

from traditional.benchmark.metrics import BenchmarkMetrics
from traditional.etl.load import get_connection
from traditional.etl.runner import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_FILE = RESULTS_DIR / "traditional_benchmark_runs.csv"


def reset_warehouse() -> None:
    """Reset the Traditional warehouse before a measured run."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE TABLE
                    traditional_dw.fact_sales,
                    traditional_dw.dim_customer,
                    traditional_dw.dim_product,
                    traditional_dw.dim_date,
                    traditional_dw.dim_country,
                    traditional_dw.pipeline_run_audit
                RESTART IDENTITY
                CASCADE;
                """
            )

        conn.commit()


def save_metrics(metrics: BenchmarkMetrics) -> None:
    """Append one benchmark observation to the results CSV."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    row = metrics.to_dict()

    file_exists = RESULTS_FILE.exists()

    with RESULTS_FILE.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=row.keys(),
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def benchmark_run(
    workload_size: int,
    run_number: int,
) -> BenchmarkMetrics:
    """Execute and measure one Traditional pipeline run."""

    # Experimental reset is outside measured execution time
    reset_warehouse()

    process = psutil.Process(os.getpid())

    memory_before = process.memory_info().rss
    cpu_before = process.cpu_times()

    start_time = datetime.now()
    start_counter = time.perf_counter()

    success = True
    error_message = None
    result = None

    try:
        result = run_pipeline(workload_size)

    except Exception as exc:
        success = False
        error_message = (
            f"{type(exc).__name__}: {exc}"
        )

    end_counter = time.perf_counter()
    end_time = datetime.now()

    cpu_after = process.cpu_times()
    memory_after = process.memory_info().rss

    execution_seconds = (
        end_counter - start_counter
    )

    cpu_time_seconds = (
        (cpu_after.user - cpu_before.user)
        + (cpu_after.system - cpu_before.system)
    )

    observed_memory_mb = (
        max(memory_before, memory_after)
        / (1024 * 1024)
    )

    if result is not None:
        records_input = result["records_input"]
        records_output = result["records_accepted"]
        records_rejected = result["records_rejected"]
        duplicates_removed = result["duplicates_removed"]

    else:
        records_input = workload_size
        records_output = 0
        records_rejected = 0
        duplicates_removed = 0

    if execution_seconds > 0:
        throughput = (
            records_input / execution_seconds
        )
    else:
        throughput = 0.0

    metrics = BenchmarkMetrics(
        architecture="Traditional",
        workload_records=workload_size,
        run_number=run_number,

        start_time=start_time,
        end_time=end_time,

        execution_seconds=execution_seconds,
        throughput_records_sec=throughput,

        records_input=records_input,
        records_output=records_output,
        records_rejected=records_rejected,
        duplicates_removed=duplicates_removed,

        success=success,
        retry_count=0,
        manual_intervention=False,

        cpu_time_seconds=cpu_time_seconds,
        peak_memory_mb=observed_memory_mb,
        error_message=error_message,
    )

    save_metrics(metrics)

    return metrics


def main() -> None:
    """Development test of benchmark instrumentation."""

    workload_size = 5_000
    run_number = 1

    print(
        f"Benchmarking Traditional pipeline: "
        f"{workload_size:,} rows"
    )

    metrics = benchmark_run(
        workload_size,
        run_number,
    )

    print()
    print("Benchmark observation:")
    print(
        f"Success:       {metrics.success}"
    )
    print(
        f"Execution:     "
        f"{metrics.execution_seconds:.4f} seconds"
    )
    print(
        f"Throughput:    "
        f"{metrics.throughput_records_sec:,.2f} "
        f"records/sec"
    )
    print(
        f"CPU time:      "
        f"{metrics.cpu_time_seconds:.4f} seconds"
    )
    print(
        f"Observed RAM:  "
        f"{metrics.peak_memory_mb:.2f} MB"
    )
    print(
        f"Input:         "
        f"{metrics.records_input:,}"
    )
    print(
        f"Output:        "
        f"{metrics.records_output:,}"
    )
    print(
        f"Rejected:      "
        f"{metrics.records_rejected:,}"
    )
    print(
        f"Duplicates:    "
        f"{metrics.duplicates_removed:,}"
    )

    if metrics.error_message:
        print(
            f"Error:         "
            f"{metrics.error_message}"
        )


if __name__ == "__main__":
    main()