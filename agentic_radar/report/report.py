import datetime
import json
import os
import math
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


def _compute_workflow_layout(graph_data: dict) -> dict:
    """Compute a layout that works well for both small and large graphs.

    - Small graphs (<= 12 nodes): compact, centered radial layout with short edges.
    - Larger graphs: deterministic workflow (level) layout with slight left shift (-50),
      matching the user's proven layout for large graphs.
    """
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])

    if not nodes:
        return graph_data

    # Helper maps
    name_to_node = {n['name']: n for n in nodes if 'name' in n}
    node_names = list(name_to_node.keys())

    # Build degree map for small-graph center choice
    degree = {name: 0 for name in node_names}
    for e in edges:
        s = e.get('source')
        t = e.get('target')
        if s in degree:
            degree[s] += 1
        if t in degree:
            degree[t] += 1

    # --- Small-graph compact layout: agent-centric radial ---
    if len(nodes) <= 12:
        # Pick a center: highest degree node; tie-break by name for determinism
        if degree:
            max_deg = max(degree.values())
            centers = [n for n, d in degree.items() if d == max_deg]
            center_name = sorted(centers)[0]
        else:
            center_name = sorted(node_names)[0]

        # Coordinates for center and ring (keep centered)
        cx, cy = 0.0, 0.0
        others = [n for n in node_names if n != center_name]
        count = max(1, len(others))
        # Radius scales slightly with node count but stays compact to shorten edges
        base_radius = 70
        radius = base_radius + max(0, (count - 4)) * 6  # grows slowly

        # Evenly distribute others around the center
        for idx, name in enumerate(others):
            angle = (2 * math.pi * idx) / count
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            node = name_to_node[name]
            node['fx'] = float(x)
            node['fy'] = float(y)

        # Place the center node
        center_node = name_to_node.get(center_name)
        if center_node is not None:
            center_node['fx'] = float(cx)
            center_node['fy'] = float(cy)

        return graph_data

    # --- Larger graphs: proven workflow layout (levels) ---
    # Build adjacency lists
    incoming = {node['name']: [] for node in nodes}
    outgoing = {node['name']: [] for node in nodes}
    for edge in edges:
        source = edge['source']
        target = edge['target']
        if source in outgoing and target in incoming:
            outgoing[source].append(target)
            incoming[target].append(source)

    # Find start/root nodes
    start_nodes = [node['name'] for node in nodes if node['name'].upper() in ['START', 'BEGIN', 'INIT']]
    roots = [name for name in incoming if len(incoming[name]) == 0]

    if start_nodes:
        primary_roots = start_nodes
    elif roots:
        primary_roots = roots
    else:
        min_incoming = min(len(incoming[name]) for name in incoming) if incoming else 0
        primary_roots = [name for name in incoming if len(incoming[name]) == min_incoming]

    # Assign workflow levels (like flowchart rows)
    levels: Dict[str, int] = {}
    queue: List[tuple[str, int]] = [(root, 0) for root in primary_roots]
    visited = set()

    while queue:
        name, level = queue.pop(0)
        if name in visited:
            continue
        visited.add(name)

        # Only assign level if not already assigned with a lower level
        if name not in levels or levels[name] > level:
            levels[name] = level

        for child in outgoing.get(name, []):
            if child not in visited:
                queue.append((child, level + 1))

    # Assign remaining nodes
    for node in nodes:
        if node['name'] not in levels:
            levels[node['name']] = 0

    # Group by levels and create workflow-style positioning
    level_groups: Dict[int, List[str]] = {}
    for name, level in levels.items():
        level_groups.setdefault(level, []).append(name)

    # Workflow layout parameters (as per user's larger-graph code)
    container_width = 800
    container_height = 400
    margin = 50

    usable_width = container_width - 2 * margin
    usable_height = container_height - 2 * margin

    sorted_levels = sorted(level_groups.keys())
    max_level = len(sorted_levels) - 1 if sorted_levels else 0

    node_positions: Dict[str, Dict[str, float]] = {}

    for i, level in enumerate(sorted_levels):
        names_at_level = level_groups[level]

        # Vertical position - distribute evenly across workflow steps
        if max_level > 0:
            y = (i / max_level) * usable_height - container_height / 2 + margin
        else:
            y = 0

        # Horizontal position - center nodes in each workflow level
        if len(names_at_level) == 1:
            x = 0
            node_positions[names_at_level[0]] = {'x': x, 'y': y}
        else:
            node_spacing = min(usable_width / (len(names_at_level) + 1), 120)
            start_x = -(len(names_at_level) - 1) * node_spacing / 2
            for j, nm in enumerate(names_at_level):
                x = start_x + j * node_spacing
                node_positions[nm] = {'x': x, 'y': y}

    # Apply a slight left shift to balance centering in the final PDF
    left_shift = -80
    for node in nodes:
        nm = node.get('name')
        if nm in node_positions:
            pos = node_positions[nm]
            node['fx'] = pos['x'] + left_shift
            node['fy'] = pos['y']

    return graph_data


def generate(graph: GraphDefinition, out_file: str, export_pdf: bool = False):
    svg = from_definition(graph).generate()

    # Parse the graph data and apply workflow-style layout
    graph_data = json.loads(svg)
    graph_data = _compute_workflow_layout(graph_data)
    svg = json.dumps(graph_data)

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

        # Try Playwright first for best fidelity
        playwright_success = False
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                # Pipe page console errors to stdout for troubleshooting
                page.on("console", lambda msg: print(f"[browser:{msg.type}] {msg.text}"))
                page.set_viewport_size({"width": 1280, "height": 900})
                # Fix Python 3.9 compatibility - prepare path outside f-string
                report_path = os.path.abspath(out_file).replace('\\', '/')
                page.goto(f"file:///{report_path}", wait_until="domcontentloaded")
                # Wait for the graph container to be present
                page.wait_for_selector('#graph', timeout=12000)
                # Wait for canvas to be added by ForceGraph
                page.wait_for_selector('#graph canvas', timeout=12000)
                # Wait until the client code signals the graph is ready (best case)
                try:
                    page.wait_for_function("window.__GRAPH_READY__ === true", timeout=9000)
                except Exception:
                    # Fallback: allow some time for forces/layout to settle
                    page.wait_for_timeout(2500)
                page.pdf(
                    path=pdf_out,
                    print_background=True,
                    format='A4',
                    margin={'top': '0.5in', 'bottom': '0.5in', 'left': '0.5in', 'right': '0.5in'}
                )
                browser.close()
            print(f"PDF report {pdf_out} generated (via Playwright)")
            playwright_success = True
        except Exception as e:
            print(f"Playwright PDF generation failed: {e}")
            # Continue to fallback methods

        # If Playwright failed, try WeasyPrint
        if not playwright_success:
            try:
                from weasyprint import HTML
                HTML(filename=out_file).write_pdf(pdf_out)
                print(f"PDF report {pdf_out} generated (via WeasyPrint)")
            except Exception as we_e:
                print(f"WeasyPrint PDF generation failed: {we_e}")
                # Final fallback: inform user about requirements
                print(
                    "PDF export failed with all methods. "
                    "For reliable PDF generation, install Playwright: 'pip install playwright && playwright install chromium'. "
                    "Alternatively, install WeasyPrint with system dependencies."
                )
