from agentic_radar.analysis.langgraph.analyze import LangGraphAnalyzer
from agentic_radar.graph import NodeType, ToolType

import pytest

@pytest.mark.supported
def test_custom_tools(tmp_path):
    """
    Custom tools defined with the @tool decorator.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langchain.tools import tool

@tool('generate_document_parsed_input_json_tool', parse_docstring=True)
def generate_document_parsed_input_json_tool(query):
    return "Custom"
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    relevant_tool_node = None

    for node in graph.tools:
        if node.node_type == NodeType.CUSTOM_TOOL and node.name == "generate_document_parsed_input_json_tool":
            relevant_tool_node = node

    assert len(graph.tools) == 1 and relevant_tool_node

@pytest.mark.supported
def test_predefined_tools(tmp_path):
    """
    Imported predefined tools.
    """
    py_file = tmp_path / "test_file.py"
    py_file.write_text("""
from langchain_community.tools import TavilySearchResults
""")

    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(str(tmp_path))

    relevant_tool_node = None

    for node in graph.tools:
        if node.node_type == NodeType.TOOL and node.category == ToolType.WEB_SEARCH and node.name == "Tavily Search":
            relevant_tool_node = node

    assert len(graph.tools) == 1 and relevant_tool_node