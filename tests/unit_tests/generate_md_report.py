import sys
import json
import os
from collections import defaultdict

GITHUB_REPO = "https://github.com/splx-ai/agentic-radar"
COMMIT_SHA = os.environ.get("GITHUB_SHA", "main")

def main(report_file: str, output_file: str = "test-report.md") -> None:
    with open(report_file, 'r') as f:
        data = json.load(f)

    tests = data['tests']

    lines = []
    lines.append("# Framework Coverage Report")
    lines.append("## Summary")

    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    total = 0
    total_supported = 0
    passed = 0
    failed = 0

    for test in tests:
        components = test["nodeid"].split("unit_tests/")[-1].split("/")
        framework = components[0]
        category = components[1]
        sub_category = components[2].split("::")[0].removesuffix(".py").removeprefix("test_")
        test_name = components[2].split("::")[1].removeprefix("test_")
        outcome = test["outcome"]
        line_number = test["lineno"]

        rel_path = f"tests/unit_tests/{framework}/{category}/test_{sub_category}.py#L{line_number}"
        test_url = f"{GITHUB_REPO}/blob/{COMMIT_SHA}/{rel_path}"

        is_supported = "supported" in test["keywords"]
        is_not_supported = "not_supported" in test["keywords"]

        total += 1
        if is_supported:
            total_supported += 1
            if outcome == "passed":
                passed += 1
                icon = "✅"
            else:
                failed += 1
                icon = "❌"
        elif is_not_supported:
            icon = "⬜"

        tree[framework][category][sub_category].append((test_name, icon, test_url))

    lines.append(f"- Total tests: {total}")
    lines.append(f"- Total supported tests: {total_supported}")
    lines.append(f"- Passed ✅: {passed}")
    lines.append(f"- Failed ❌: {failed}")
    lines.append("")

    lines.append("## Tests")
    for framework, categories in tree.items():
        lines.append(f"- **{framework}**")
        for category, sub_categories in categories.items():
            lines.append(f"  - **{category}**")
            for sub_category, tests in sub_categories.items():
                lines.append(f"    - **{sub_category}**")
                for test_name, result_icon, test_url in tests:
                    lines.append(f"      - [{test_name}]({test_url}) {result_icon}")

    # Write to file using UTF-8 encoding
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    main(sys.argv[1])