import os
import pytest

from collections import defaultdict

FRAMEWORK_NAME_MAPPING = {
    "langgraph": "LangGraph",
    "crewai": "CrewAI",
    "n8n": "n8n",
    "openai-agents": "OpenAI Agents"
}

test_metadata = {}
all_results = defaultdict(list)

def pytest_runtest_protocol(item, nextitem):
    test_metadata[item.nodeid] = {
        "docstring": item.obj.__doc__,
        "markers": [m.name for m in item.iter_markers()],
        "lineno": item.obj.__code__.co_firstlineno + 1
    }
    return None

def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    meta = test_metadata.get(report.nodeid) or {}
    markers = meta.get("markers", [])
    docstring = (meta.get("docstring") or "").replace("\n", "")
    lineno = meta.get("lineno", 0)

    relative_nodeid = report.nodeid.split("unit_tests/")[-1]
    path_parts = relative_nodeid.split("/")
    framework_key = path_parts[0].split("::")[0]
    framework = FRAMEWORK_NAME_MAPPING.get(framework_key, "General")

    if len(path_parts) > 1:
        category = path_parts[1]
    else:
        file_part = path_parts[0].split("::")[0]
        category = os.path.splitext(os.path.basename(file_part))[0] or "general"

    outcome = "Unknown"
    url = report.nodeid.split("::")[0] + f"#L{lineno}"

    if "supported" in markers:
        if report.outcome == "passed":
            outcome = "Passed✅"
        elif report.outcome == "failed":
            outcome = "Failed❌"
    elif "not_supported" in markers:
        outcome = "Unsupported⬜"

    result = {
        "docstring": docstring,
        "outcome": outcome,
        "url": url,
        "category": category
    }

    all_results[framework].append(result)

def pytest_sessionfinish(session, exitstatus):
    with open("test-report.md", "w", encoding="utf-8") as f:
        for framework, results in all_results.items():
            f.write(f"# {framework} Tests\n")
            f.write("| Category | Test Description | Status | Link |\n")
            f.write("|----------|------------------|--------|------|\n")

            results_by_category = defaultdict(list)
            for result in results:
                results_by_category[result["category"]].append(result)

            for category in sorted(results_by_category.keys()):
                category_results = results_by_category[category]
                first = True
                for result in category_results:
                    cat_cell = category if first else ""
                    f.write(f"| {cat_cell} | {result['docstring']} | {result['outcome']} | [link]({result['url']}) |\n")
                    first = False