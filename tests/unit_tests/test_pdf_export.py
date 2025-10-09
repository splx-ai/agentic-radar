import os
from unittest import mock

from agentic_radar.report import GraphDefinition, NodeDefinition, EdgeDefinition, generate


def make_minimal_graph():
    gd = GraphDefinition(
        name="test",
        framework="langgraph",
        nodes=[NodeDefinition(name="A", node_type="basic"), NodeDefinition(name="B", node_type="basic")],
        edges=[EdgeDefinition(start="A", end="B")],
    )
    return gd


def test_generate_html_and_pdf_fallback(tmp_path):
    out_html = str(tmp_path / "out.html")

    gd = make_minimal_graph()

    # Mock Playwright to be unavailable and provide mocked weasyprint
    with mock.patch.dict('sys.modules', {'playwright.sync_api': None}):
        fake_html = mock.MagicMock()
        fake_html.write_pdf = mock.MagicMock()
        mock_weasy = mock.MagicMock(HTML=lambda filename: fake_html)
        with mock.patch.dict('sys.modules', {'weasyprint': mock_weasy}):
            generate(gd, out_html, export_pdf=True)

    # HTML should be written
    assert os.path.exists(out_html)
