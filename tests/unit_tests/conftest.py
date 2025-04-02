import os
import pytest

from collections import defaultdict

GITHUB_REPO = "https://github.com/splx-ai/agentic-radar"
COMMIT_SHA = os.environ.get("GITHUB_SHA", "main")
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
    if report.when == "call":
        meta = test_metadata.get(report.nodeid, {})

        markers = meta.get("markers", [])
        docstring = meta.get("docstring", "")
        lineno = meta.get("lineno", 0)
        framework = FRAMEWORK_NAME_MAPPING.get(report.nodeid.removeprefix("tests/unit_tests/").split("/")[0], "Unknown (error while mapping name)")
        category = report.nodeid.split("unit_tests/")[-1].split("/")[1]
        docstring = meta.get("docstring", "").replace("\n", "")
        outcome = "Unknown"
        url = f"{GITHUB_REPO}/blob/{COMMIT_SHA}/{report.nodeid.split('::')[0] + f'#L{lineno}'}"

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
            # f.write("| Test Description | Status | Link |\n")
            # f.write("|------|--------|---------|\n")
            # for result in results:
            #     f.write(f"| {result['docstring']} | {result['outcome']} | [link]({result['url']}) |\n")
            f.write("| Category | Test Description | Status | Link |\n")
            f.write("|----------|------------------|--------|------|\n")

            # Group results by category
            results_by_category = defaultdict(list)
            for result in results:
                results_by_category[result["category"]].append(result)

            # Sort categories for consistent output
            for category in sorted(results_by_category.keys()):
                category_results = results_by_category[category]
                first = True
                for result in category_results:
                    cat_cell = category if first else ""  # Print category only once
                    f.write(f"| {cat_cell} | {result['docstring']} | {result['outcome']} | [link]({result['url']}) |\n")
                    first = False