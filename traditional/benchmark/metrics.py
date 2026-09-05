from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BenchmarkMetrics:
    architecture: str
    workload_records: int
    run_number: int

    start_time: datetime
    end_time: datetime

    execution_seconds: float
    throughput_records_sec: float

    records_input: int
    records_output: int
    records_rejected: int
    duplicates_removed: int

    success: bool
    retry_count: int
    manual_intervention: bool

    cpu_time_seconds: float | None = None
    peak_memory_mb: float | None = None
    error_message: str | None = None


    extract_seconds: float | None = None
    transform_seconds: float | None = None
    prepare_seconds: float | None = None
    load_seconds: float | None = None


    ingestion_seconds: float | None = None
    validation_seconds: float | None = None
    staging_seconds: float | None = None
    intermediate_seconds: float | None = None
    marts_seconds: float | None = None

    
    orchestration_overhead_seconds: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)