import argparse
import csv
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

from traditional.etl.load import get_connection
from traditional.benchmark.metrics import BenchmarkMetrics


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_FILE = RESULTS_DIR / "modern_benchmark_runs.csv"

AIRFLOW_DIR = PROJECT_ROOT / "modern" / "airflow"

DAG_ID = "modern_pipeline_benchmark"


def trigger_dag(
    workload_size: int,
    run_number: int,
) -> str:
    """Trigger one normal Airflow DAG run and return its run ID."""

    run_id = (
        f"benchmark_{workload_size}_"
        f"run_{run_number}_"
        f"{int(time.time())}"
    )

    conf = json.dumps(
        {
            "workload_size": workload_size,
        }
    )

    command = [
        "docker",
        "compose",
        "exec",
        "-T",
        "airflow-scheduler",
        "airflow",
        "dags",
        "trigger",
        DAG_ID,
        "--run-id",
        run_id,
        "--conf",
        conf,
    ]

    subprocess.run(
        command,
        cwd=AIRFLOW_DIR,
        check=True,
    )

    return run_id


def get_dag_state(run_id: str) -> str | None:
    """Read the current state of an Airflow DAG run."""

    command = [
        "docker",
        "compose",
        "exec",
        "-T",
        "airflow-scheduler",
        "airflow",
        "dags",
        "list-runs",
        DAG_ID,
        "--output",
        "json",
    ]

    result = subprocess.run(
        command,
        cwd=AIRFLOW_DIR,
        check=True,
        capture_output=True,
        text=True,
    )

    runs = json.loads(result.stdout)

    for dag_run in runs:
        if dag_run.get("run_id") == run_id:
            return dag_run.get("state")

    return None



def get_task_durations(run_id: str) -> dict:
    """Return Airflow task durations for one benchmark DAG run."""

    command = [
        "docker",
        "compose",
        "exec",
        "-T",
        "airflow-scheduler",
        "airflow",
        "tasks",
        "states-for-dag-run",
        DAG_ID,
        run_id,
        "--output",
        "json",
    ]

    result = subprocess.run(
        command,
        cwd=AIRFLOW_DIR,
        check=True,
        capture_output=True,
        text=True,
    )

    tasks = json.loads(result.stdout)

    durations = {}

    for task in tasks:
        task_id = task.get("task_id")
        start_date = task.get("start_date")
        end_date = task.get("end_date")

        if (
            task_id
            and start_date
            and end_date
        ):
            start = datetime.fromisoformat(
                start_date
            )

            end = datetime.fromisoformat(
                end_date
            )

            durations[task_id] = (
                end - start
            ).total_seconds()

    return durations



'''def get_task_durations(run_id: str) -> dict:
    """Return measured Airflow task durations for one benchmark DAG run."""

    command = [
        "docker",
        "compose",
        "exec",
        "-T",
        "airflow-scheduler",
        "airflow",
        "tasks",
        "states-for-dag-run",
        DAG_ID,
        run_id,
        "--output",
        "json",
    ]

    result = subprocess.run(
        command,
        cwd=AIRFLOW_DIR,
        check=True,
        capture_output=True,
        text=True,
    )

    tasks = json.loads(result.stdout)

    durations = {}

    for task in tasks:
        task_id = task.get("task_id")
        duration = task.get("duration")

        if duration is not None:
            durations[task_id] = float(duration)

    return durations'''

def wait_for_dag(
    run_id: str,
    timeout_seconds: int = 600,
) -> str:
    """Wait until the DAG reaches a terminal state."""

    start = time.monotonic()

    while True:
        state = get_dag_state(run_id)

        print(
            f"Airflow run {run_id}: "
            f"{state}"
        )

        if state in {
            "success",
            "failed",
        }:
            return state

        if (
            time.monotonic() - start
            > timeout_seconds
        ):
            raise TimeoutError(
                f"Airflow DAG {run_id} did not finish "
                f"within {timeout_seconds} seconds."
            )

        time.sleep(2)


def read_pipeline_counts() -> dict:
    """Read Modern pipeline accounting results."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    records_input,
                    records_accepted,
                    records_rejected,
                    duplicates_removed
                FROM modern_dw.quality_summary
                LIMIT 1;
                """
            )

            row = cur.fetchone()

    if row is None:
        raise RuntimeError(
            "Modern quality_summary returned no row."
        )

    return {
        "records_input": row[0],
        "records_output": row[1],
        "records_rejected": row[2],
        "duplicates_removed": row[3],
    }


def save_metrics(metrics: BenchmarkMetrics) -> None:
    """Append one Modern benchmark observation."""

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


def reset_modern() -> None:
    """Reset Modern raw and warehouse objects before a measured run."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE TABLE
                    modern_raw.online_retail_raw
                RESTART IDENTITY
                CASCADE;
                """
            )

            cur.execute(
                """
                DROP TABLE IF EXISTS
                    modern_dw.dim_customer,
                    modern_dw.dim_product,
                    modern_dw.dim_date,
                    modern_dw.dim_country,
                    modern_dw.fact_sales
                CASCADE;
                """
            )

            cur.execute(
                """
                DROP VIEW IF EXISTS
                    modern_dw.stg_online_retail,
                    modern_dw.int_classified_records,
                    modern_dw.int_accepted_records,
                    modern_dw.int_rejected_records,
                    modern_dw.int_duplicate_records
                CASCADE;
                """
            )

        conn.commit()


def benchmark_run(
    workload_size: int,
    run_number: int,
) -> BenchmarkMetrics:
    """Execute and measure one Modern Airflow/dbt pipeline."""


    # Reset is outside the measured execution boundary
    reset_modern()

    # Initialise values so they always exist,
    # even if the DAG fails before completion.
    
    validation_seconds = None
    run_id = None
    counts = None
    task_durations = {}

    ingestion_seconds = None
    staging_seconds = None
    intermediate_seconds = None
    marts_seconds = None
    orchestration_overhead_seconds = None

    success = True
    error_message = None

    start_time = datetime.now()
    start_counter = time.perf_counter()

    try:
        run_id = trigger_dag(
            workload_size,
            run_number,
        )

        state = wait_for_dag(run_id)

        if state != "success":
            raise RuntimeError(
                f"Airflow DAG finished with state: {state}"
            )

        counts = read_pipeline_counts()

    except Exception as exc:
        success = False
        error_message = (
            f"{type(exc).__name__}: {exc}"
        )

    end_counter = time.perf_counter()
    end_time = datetime.now()

    execution_seconds = (
        end_counter - start_counter
    )

    # Retrieve individual Airflow task durations
    # only if a DAG run was actually created.
    if run_id is not None:
        try:
            task_durations = get_task_durations(
                run_id
            )


            ingestion_seconds = (
                task_durations.get(
                    "ingest_workload"
                )
            )

            staging_seconds = (
                task_durations.get(
                    "dbt_staging"
                )
            )

            intermediate_seconds = (
                task_durations.get(
                    "dbt_intermediate"
                )
            )

            marts_seconds = (
                task_durations.get(
                    "dbt_marts"
                )
            )
            ingestion_seconds = task_durations.get(
                "ingest_workload"
            )

            validation_seconds = task_durations.get(
                "validate_raw_count"
            )

            staging_seconds = task_durations.get(
                "dbt_staging"
            )

            intermediate_seconds = task_durations.get(
                "dbt_intermediate"
            )

            marts_seconds = task_durations.get(
                "dbt_marts"
            )
    
           

        except Exception as exc:
            # Do not invalidate the whole pipeline run
            # just because component timing retrieval failed.
            print(
                "Warning: unable to retrieve "
                f"task durations: {exc}"
            )

    # Calculate orchestration / transition overhead
    component_times = [
        ingestion_seconds,
        validation_seconds,
        staging_seconds,
        intermediate_seconds,
        marts_seconds,
    ]

    if all(
        value is not None
        for value in component_times
    ):
        orchestration_overhead_seconds = (
            execution_seconds
            - sum(component_times)
        )

    # Pipeline accounting
    if counts is not None:
        records_input = (
            counts["records_input"]
        )
        records_output = (
            counts["records_output"]
        )
        records_rejected = (
            counts["records_rejected"]
        )
        duplicates_removed = (
            counts["duplicates_removed"]
        )

    else:
        records_input = workload_size
        records_output = 0
        records_rejected = 0
        duplicates_removed = 0

    # Throughput
    if execution_seconds > 0:
        throughput = (
            records_input
            / execution_seconds
        )
    else:
        throughput = 0.0

    metrics = BenchmarkMetrics(
        architecture="Modern",
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

        # Docker resource measurement uses a
        # different measurement boundary, so
        # these remain unset for the Modern run.
        cpu_time_seconds=None,
        peak_memory_mb=None,

        # Traditional-only component timings
        extract_seconds=None,
        transform_seconds=None,
        prepare_seconds=None,
        load_seconds=None,
    
        # Modern component timings
        ingestion_seconds=ingestion_seconds,
        staging_seconds=staging_seconds,
        intermediate_seconds=intermediate_seconds,
        marts_seconds=marts_seconds,
        validation_seconds=validation_seconds,
        orchestration_overhead_seconds=(
            orchestration_overhead_seconds
        ),

        error_message=error_message,
    )

    save_metrics(metrics)

    return metrics

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark the Modern Airflow/dbt pipeline."
    )

    parser.add_argument(
        "--records",
        type=int,
        required=True,
        choices=[
            5_000,
            10_000,
            50_000,
            100_000,
        ],
        help="Workload size to benchmark.",
    )

    parser.add_argument(
        "--run",
        type=int,
        required=True,
        help="Benchmark repetition number.",
    )

    args = parser.parse_args()

    print(
        f"Benchmarking Modern pipeline: "
        f"{args.records:,} rows "
        f"(run {args.run})"
    )

    metrics = benchmark_run(
        workload_size=args.records,
        run_number=args.run,
    )

    print()
    print("Benchmark observation:")
    print(f"Success:       {metrics.success}")
    print(
        f"Execution:     "
        f"{metrics.execution_seconds:.4f} seconds"
    )
    print(
        f"Throughput:    "
        f"{metrics.throughput_records_sec:,.2f} "
        f"records/sec"
    )
    print(f"Input:         {metrics.records_input:,}")
    print(f"Output:        {metrics.records_output:,}")
    print(f"Rejected:      {metrics.records_rejected:,}")
    print(f"Duplicates:    {metrics.duplicates_removed:,}")

    if metrics.error_message:
        print(
            f"Error:         "
            f"{metrics.error_message}"
        )


if __name__ == "__main__":
    main()