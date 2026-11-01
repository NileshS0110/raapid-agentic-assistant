
import json
import shutil
import statistics
import time

from pathlib import Path

from app.orchestrator import process_employee_request


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TICKETS_FILE = BASE_DIR / "data" / "tickets.json"
BACKUP_FILE = BASE_DIR / "data" / "tickets_benchmark_backup.json"

RESULTS_FILE = BASE_DIR / "evals" / "performance_results.json"

REPEATS = 5


# --------------------------------------------------
# BENCHMARK SCENARIOS
# --------------------------------------------------

SCENARIOS = {
    "policy_query": (
        "How many annual paid leave days do employees get?"
    ),
    "record_query": (
        "What is my leave balance?"
    ),
    "ticket_creation": (
        "Raise a ticket for my laptop issue."
    )
}


# --------------------------------------------------
# MEASUREMENT FUNCTION
# --------------------------------------------------

def measure_scenario(name, question):

    timings = []
    statuses = []

    print(f"\nBenchmarking: {name}")

    for run_number in range(1, REPEATS + 1):

        start_time = time.perf_counter()

        response = process_employee_request(question)

        elapsed = time.perf_counter() - start_time

        elapsed_ms = round(elapsed * 1000, 2)

        timings.append(elapsed_ms)

        # process_employee_request returns a dictionary.
        status = response.get("status", "unknown")

        statuses.append(status)

        print(
            f"Run {run_number}: "
            f"{elapsed_ms} ms | "
            f"Status: {status}"
        )

    return {
        "scenario": name,
        "runs": REPEATS,
        "latency_ms": timings,
        "median_latency_ms": round(
            statistics.median(timings), 2
        ),
        "worst_case_latency_ms": round(
            max(timings), 2
        ),
        "best_case_latency_ms": round(
            min(timings), 2
        ),
        "statuses": statuses
    }


# --------------------------------------------------
# MAIN BENCHMARK
# --------------------------------------------------

def run_benchmark():

    results = []

    # Back up the original ticket data.
    shutil.copy2(TICKETS_FILE, BACKUP_FILE)

    try:

        # Policy query: invokes local LLM.
        results.append(
            measure_scenario(
                "policy_query",
                SCENARIOS["policy_query"]
            )
        )

        # Structured record query.
        results.append(
            measure_scenario(
                "record_query",
                SCENARIOS["record_query"]
            )
        )

        # Ticket creation.
        results.append(
            measure_scenario(
                "ticket_creation",
                SCENARIOS["ticket_creation"]
            )
        )

    finally:

        # Restore original ticket data.
        if BACKUP_FILE.exists():
            shutil.copy2(BACKUP_FILE, TICKETS_FILE)
            BACKUP_FILE.unlink()

    # --------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------

    summary = {
        "measurement_type": "Local prototype benchmark",
        "repeats_per_scenario": REPEATS,
        "results": results
    }

    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4
        )

    # --------------------------------------------------
    # PRINT SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)

    for item in results:

        print(f"\nScenario: {item['scenario']}")

        print(
            "Median:",
            item["median_latency_ms"],
            "ms"
        )

        print(
            "Worst case:",
            item["worst_case_latency_ms"],
            "ms"
        )

        print(
            "Best case:",
            item["best_case_latency_ms"],
            "ms"
        )

        print("Statuses:", item["statuses"])

    print("\nResults saved to:", RESULTS_FILE)

    print("\nBenchmark completed.")


if __name__ == "__main__":
    run_benchmark()
