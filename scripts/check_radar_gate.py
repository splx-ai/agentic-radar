import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_radar_gate.py <path-to-results.json>")
        sys.exit(1)

    results_path = Path(sys.argv[1])
    if not results_path.exists():
        print(f"[Gate Error] Results file not found: {results_path}")
        sys.exit(1)

    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[Gate Error] Invalid JSON in {results_path}: {exc}")
        sys.exit(1)

    # Support both a flat list of test results and a {"summary": ..., "results": [...]} dict
    if isinstance(data, list):
        results = data
        total = len(results)
        passed = sum(1 for item in results if item.get("test_passed") is True)
        failed = total - passed
    elif isinstance(data, dict):
        results = data.get("results", [])
        summary = data.get("summary", {})
        total = summary.get("total", len(results))
        passed = summary.get("passed", sum(1 for item in results if item.get("test_passed") is True))
        failed = summary.get("failed", total - passed)
    else:
        print("[Gate Error] Unexpected JSON structure.")
        sys.exit(1)

    print("=== Agentic Radar Security Gate Summary ===")
    print(f"Total:  {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed tests:")
        for item in results:
            if not item.get("test_passed", False):
                agent = item.get("agent_name", "Unknown Agent")
                test_name = item.get("test_name", "Unknown Test")
                print(f"  - {agent} | {test_name}")
        print("\n[BLOCKED] Security gate failed: vulnerabilities detected.")
        sys.exit(1)

    print("\n[PASSED] Security gate passed: all tests succeeded.")
    sys.exit(0)


if __name__ == "__main__":
    main()