
import json
import time
import sys
from pathlib import Path
from collections import defaultdict

from app.orchestrator import process_employee_request
from app import orchestrator
from app.tools import (
    get_leave_balance,
    ToolError,
    AuthorizationError
)
from app.action_tools import create_ticket


BASE_DIR = Path(__file__).resolve().parent.parent

EVAL_FILE = BASE_DIR / "evals" / "evaluation_suite.json"
RESULTS_FILE = BASE_DIR / "evals" / "raw_results.json"
THRESHOLDS_FILE = BASE_DIR / "evals" / "evaluation_thresholds.json"


def load_suite():
    """Load the evaluation scenarios."""

    with open(EVAL_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_thresholds():
    """Load predefined evaluation acceptance thresholds."""

    with open(THRESHOLDS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def run_direct_tool_test(scenario):
    """Execute scenarios that test tools directly."""

    tool = scenario["tool"]

    try:

        if tool == "get_leave_balance":

            session_id = scenario.get("session_employee_id")
            requested_id = scenario.get("requested_employee_id")

            get_leave_balance(
                session_id,
                requested_id
            )

            return {
                "status": "success",
                "details": {}
            }

        if tool == "create_ticket":

            priority = scenario.get("priority", "Medium")

            request_id = scenario.get(
                "request_id",
                "EVAL-" + str(time.time_ns())
            )

            # First attempt.
            create_ticket(
                session_employee_id="EMP001",
                title="Evaluation ticket",
                description="Ticket created for evaluation.",
                priority=priority,
                request_id=request_id
            )

            # Second attempt checks duplicate prevention.
            second = create_ticket(
                session_employee_id="EMP001",
                title="Evaluation ticket",
                description="Ticket created for evaluation.",
                priority=priority,
                request_id=request_id
            )

            if second.get("duplicate_prevented"):
                return {
                    "status": "duplicate_prevented",
                    "details": second
                }

            return {
                "status": "success",
                "details": second
            }

        return {
            "status": "unsupported_test",
            "details": {}
        }

    except AuthorizationError as error:

        return {
            "status": "access_denied",
            "details": {"error": str(error)}
        }

    except ValueError as error:

        return {
            "status": "validation_error",
            "details": {"error": str(error)}
        }

    except ToolError as error:

        return {
            "status": "tool_failure",
            "details": {"error": str(error)}
        }


def execute_scenario(scenario):
    """Run one scenario and capture its actual response."""

    start_time = time.perf_counter()

    try:

        if scenario.get("test_method") == "direct_tool":

            response = run_direct_tool_test(scenario)

        else:

            # Simulate a ticketing system failure when requested.
            if scenario.get("simulate_failure"):

                original_create_ticket = orchestrator.create_ticket

                def failing_create_ticket(*args, **kwargs):
                    raise ToolError(
                        "Simulated ticketing system failure."
                    )

                orchestrator.create_ticket = failing_create_ticket

                try:
                    response = process_employee_request(
                        scenario["input"]
                    )
                finally:
                    orchestrator.create_ticket = original_create_ticket

            else:

                response = process_employee_request(
                    scenario["input"]
                )

        return response, round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

    except Exception as error:

        return {
            "status": "execution_error",
            "message": str(error)
        }, round(
            (time.perf_counter() - start_time) * 1000,
            2
        )


def check_scenario(scenario, response):
    """Apply deterministic assertions to the response."""

    checks = {}

    expected_status = scenario.get("expected_status")
    actual_status = response.get("status")

    checks["status"] = (
        actual_status == expected_status
    )

    if scenario.get("expected_route"):

        actual_route = response.get("route")

        checks["route"] = (
            actual_route == scenario["expected_route"]
        )

    response_text = json.dumps(
        response,
        ensure_ascii=False
    ).lower()

    for term in scenario.get("required_terms", []):

        checks[f"required_term:{term}"] = (
            term.lower() in response_text
        )

    for term in scenario.get("forbidden_terms", []):

        checks[f"forbidden_term:{term}"] = (
            term.lower() not in response_text
        )

    citations = response.get("citations", [])

    cited_document_ids = []

    for citation in citations:

        if isinstance(citation, dict):

            cited_document_ids.append(
                citation.get("document_id", "")
            )

        elif isinstance(citation, str):

            cited_document_ids.append(citation)

    for document_id in scenario.get("required_citations", []):

        checks[f"required_citation:{document_id}"] = (
            document_id in cited_document_ids
        )

    for document_id in scenario.get("forbidden_citations", []):

        checks[f"forbidden_citation:{document_id}"] = (
            document_id not in cited_document_ids
        )

    if "requires_human_review" in scenario:

        checks["human_review"] = (
            response.get("requires_human_review")
            == scenario["requires_human_review"]
        )

    passed = all(checks.values()) if checks else False

    return passed, checks


def run_evaluation():
    """Run scenarios and enforce predefined acceptance thresholds."""

    suite = load_suite()
    thresholds = load_thresholds()

    results = []

    print("\n" + "=" * 75)
    print("EMPLOYEE AI ASSISTANT - EVALUATION")
    print("=" * 75)

    # Run each evaluation scenario.
    for scenario in suite["scenarios"]:

        scenario_id = scenario["id"]

        print(
            f"\nRunning {scenario_id}: "
            f"{scenario['category']}"
        )

        response, latency_ms = execute_scenario(scenario)

        passed, checks = check_scenario(
            scenario,
            response
        )

        result = {
            "id": scenario_id,
            "category": scenario["category"],
            "mandatory": scenario.get("mandatory", False),
            "input": scenario.get("input", ""),
            "expected_status": scenario["expected_status"],
            "actual_status": response.get("status"),
            "expected_route": scenario.get("expected_route"),
            "actual_route": response.get("route"),
            "passed": passed,
            "checks": checks,
            "latency_ms": latency_ms,
            "actual_response": response
        }

        results.append(result)

        label = "PASS" if passed else "FAIL"

        print(f"Result: {label}")

        for check_name, check_result in checks.items():

            print(
                f"  {'PASS' if check_result else 'FAIL'} "
                f"- {check_name}"
            )

    # Calculate overall metrics.
    total = len(results)

    passed_count = sum(
        1 for result in results if result["passed"]
    )

    failed_count = total - passed_count

    pass_rate = (
        passed_count / total * 100
        if total else 0
    )

    # Calculate pass rate by evaluation dimension.
    dimension_results = defaultdict(list)

    for result in results:

        dimension_results[result["category"]].append(
            result["passed"]
        )

    dimension_scores = {}

    for category, values in dimension_results.items():

        dimension_scores[category] = {
            "passed": sum(values),
            "total": len(values),
            "pass_rate_percent": round(
                sum(values) / len(values) * 100,
                2
            )
        }

    # Calculate mandatory scenario results.
    mandatory_results = [
        result for result in results
        if result["mandatory"]
    ]

    mandatory_passed = sum(
        1 for result in mandatory_results
        if result["passed"]
    )

    mandatory_pass_rate = (
        mandatory_passed / len(mandatory_results) * 100
        if mandatory_results else 0
    )

    # Calculate critical security scenario results.
    results_by_id = {
        result["id"]: result for result in results
    }

    critical_ids = thresholds["critical_security_scenario_ids"]

    missing_critical_ids = [
        scenario_id
        for scenario_id in critical_ids
        if scenario_id not in results_by_id
    ]

    critical_results = [
        results_by_id[scenario_id]
        for scenario_id in critical_ids
        if scenario_id in results_by_id
    ]

    critical_passed = sum(
        1 for result in critical_results
        if result["passed"]
    )

    critical_pass_rate = (
        critical_passed / len(critical_ids) * 100
        if critical_ids else 0
    )

    # Enforce predefined acceptance thresholds.
    threshold_checks = {
        "overall_pass_rate": (
            pass_rate >= thresholds["overall_pass_rate_percent_min"]
        ),

        "mandatory_scenarios": (
            mandatory_pass_rate
            >= thresholds["mandatory_pass_rate_percent_min"]
            and len(mandatory_results) > 0
        ),

        "critical_security_scenarios": (
            critical_pass_rate
            >= thresholds["critical_security_pass_rate_percent_min"]
            and len(missing_critical_ids) == 0
            and len(critical_ids) > 0
        )
    }

    acceptance_passed = all(threshold_checks.values())

    # Prepare complete evaluation summary.
    summary = {
        "suite_name": suite["suite_name"],
        "total_scenarios": total,
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate_percent": round(pass_rate, 2),

        "mandatory_scenarios_total": len(mandatory_results),
        "mandatory_scenarios_passed": mandatory_passed,
        "mandatory_pass_rate_percent": round(
            mandatory_pass_rate, 2
        ),

        "critical_security_scenarios_total": len(critical_ids),
        "critical_security_scenarios_passed": critical_passed,
        "critical_security_pass_rate_percent": round(
            critical_pass_rate, 2
        ),
        "missing_critical_scenario_ids": missing_critical_ids,

        "dimension_scores": dimension_scores,

        "acceptance_thresholds": thresholds,
        "threshold_checks": threshold_checks,
        "acceptance_passed": acceptance_passed,

        "results": results
    }

    # Save raw results.
    with open(RESULTS_FILE, "w", encoding="utf-8") as file:

        json.dump(
            summary,
            file,
            indent=2,
            ensure_ascii=False
        )

    # Print evaluation summary.
    print("\n" + "=" * 75)
    print("EVALUATION SUMMARY")
    print("=" * 75)

    print(f"Total scenarios: {total}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Overall pass rate: {pass_rate:.2f}%")

    print(
        f"Mandatory scenarios passed: "
        f"{mandatory_passed}/{len(mandatory_results)} "
        f"({mandatory_pass_rate:.2f}%)"
    )

    print(
        f"Critical security scenarios passed: "
        f"{critical_passed}/{len(critical_ids)} "
        f"({critical_pass_rate:.2f}%)"
    )

    print("\nPass rate by dimension:")

    for category, score in dimension_scores.items():

        print(
            f"{category}: "
            f"{score['passed']}/{score['total']} "
            f"({score['pass_rate_percent']}%)"
        )

    print("\nAcceptance threshold checks:")

    for name, passed in threshold_checks.items():

        print(
            f"{'PASS' if passed else 'FAIL'} - {name}"
        )

    print("\n" + "=" * 75)

    print(
        "FINAL ACCEPTANCE: "
        + ("PASS" if acceptance_passed else "FAIL")
    )

    print("=" * 75)

    print("\nRaw results saved to:")
    print(RESULTS_FILE)

    return summary


if __name__ == "__main__":

    summary = run_evaluation()

    # Return a non-zero exit code if acceptance criteria fail.
    if not summary["acceptance_passed"]:
        sys.exit(1)
