import datetime
import json
import os
from typing import Dict, List, Optional

import importlib_resources as resources
import jinja2
from pydantic import BaseModel, Field

from agentic_radar import __version__

from ..graph import Agent, NodeType
from .graph import (
    GraphDefinition,
    from_definition,
)


class Vulnerability(BaseModel):
    name: str
    description: str
    security_framework_mapping: Dict[str, str]
    remediation: str


class Tool(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    vulnerabilities: List[Vulnerability] = Field(default_factory=list)


class MCPServer(BaseModel):
    name: str
    description: str


class ReportData(BaseModel):
    project_name: str
    framework: str
    timestamp: str
    graph: str

    count: Dict[str, int]

    agents: List[Agent]
    tools: List[Tool]
    mcp_servers: List[MCPServer]
    hardened_prompts: Dict[str, str]
    scanner_version: str

    force_graph_dependency_path: str


def generate(graph: GraphDefinition, out_file: str, export_pdf: bool = False):
    svg = from_definition(graph).generate()

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates")
        )
    )

    template = env.get_template("template.html.jinja")
    agents = [Agent.model_validate(a, from_attributes=True) for a in graph.agents]
    tools = [Tool.model_validate(t, from_attributes=True) for t in graph.tools]
    mcp_servers = [
        MCPServer(name=node.name, description=node.description or "")
        for node in graph.nodes
        if node.node_type == NodeType.MCP_SERVER
    ]

    with open(
        os.path.join(
            os.path.dirname(__file__), "templates", "assets", "vulnerabilities.json"
        )
    ) as f:
        vulnerability_definitions = json.load(f)

    template.stream(
        **ReportData(
            project_name=graph.name,
            framework=graph.framework,
            timestamp=datetime.datetime.now().strftime("%x %X"),
            graph=svg,
            count={
                "tools": len(tools),
                "agents": len(
                    [x for x in graph.nodes if x.node_type == NodeType.AGENT]
                ),
                "vulnerability": len(
                    [v for t in graph.tools for v in t.vulnerabilities]
                ),
            },
            agents=agents,
            tools=tools,
            mcp_servers=mcp_servers,
            hardened_prompts=graph.hardened_prompts,
            scanner_version=__version__,
            force_graph_dependency_path=str(
                resources.files(__package__) / "templates" / "assets" / "force-graph.js"
            ),
        ).model_dump(),
        vulnerability_definitions=vulnerability_definitions,
    ).dump(out_file)
    # If PDF export requested, try to convert the generated HTML to PDF.
    if export_pdf:
        # Try a headless browser-based conversion first (Playwright), since the report
        # relies on client-side JS to render the graph. If Playwright isn't available or
        # fails, fall back to WeasyPrint which does not execute JS but works for static content.
        pdf_out = out_file if out_file.lower().endswith('.pdf') else os.path.splitext(out_file)[0] + '.pdf'
        # Playwright path
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(f"file:///{os.path.abspath(out_file).replace('\\', '/')}", wait_until="networkidle")
                # Give the force-graph some time to render
                page.wait_for_timeout(1000)
                page.pdf(path=pdf_out, print_background=True)
                browser.close()
            print(f"PDF report {pdf_out} generated (via Playwright)")
            return
        except Exception:
            # Ignore and try WeasyPrint fallback
            pass

        # WeasyPrint fallback (no JS execution)
        try:
            from weasyprint import HTML

            HTML(filename=out_file).write_pdf(pdf_out)
            print(f"PDF report {pdf_out} generated (via WeasyPrint)")
        except Exception as e:
            # We avoid crashing; provide a helpful message.
            print(
                "PDF export requested but conversion failed. "
                "For faithful rendering (including JS graphs) install Playwright and browser binaries: 'pip install \"agentic-radar[pdf-browser]\"' and run 'playwright install'. "
                "Alternatively, install WeasyPrint with system dependencies: 'pip install \"agentic-radar[pdf]\"'."
            )
            print(f"Conversion error: {e}")
