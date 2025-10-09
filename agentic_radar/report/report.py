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
    report_intro: Optional[str] = None

    force_graph_dependency_path: str


def _compute_workflow_layout(graph_data: dict) -> dict:
    """Deterministic hierarchical workflow layout with adaptive compression.

    Goals:
    - Keep graph fully visible (no clipping) regardless of node count.
    - Minimize vertical span while preserving readable separation.
    - Provide minimum horizontal spread to avoid over-zoom tiny graphs.
    - Stable ordering per level (alphabetical fallback) for reproducibility.
    """
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    if not nodes:
        return graph_data

    # Build adjacency
    incoming: Dict[str, List[str]] = {n["name"]: [] for n in nodes if "name" in n}
    outgoing: Dict[str, List[str]] = {n["name"]: [] for n in nodes if "name" in n}
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if s in outgoing and t in incoming:
            outgoing[s].append(t)
            incoming[t].append(s)

    # Roots detection: explicit START-like else zero incoming else min incoming.
    start_aliases = {"START", "BEGIN", "INIT"}
    roots = [n for n in incoming if n.upper() in start_aliases] or [n for n, v in incoming.items() if not v]
    if not roots:
        min_in_deg = min(len(v) for v in incoming.values()) if incoming else 0
        roots = [n for n, v in incoming.items() if len(v) == min_in_deg]

    # BFS levels
    levels: Dict[str, int] = {}
    queue: List[tuple[str, int]] = [(r, 0) for r in roots]
    seen = set()
    while queue:
        name, lvl = queue.pop(0)
        if name in seen:
            continue
        seen.add(name)
        levels[name] = min(lvl, levels.get(name, lvl))
        for ch in outgoing.get(name, []):
            if ch not in seen:
                queue.append((ch, lvl + 1))
    # Orphans -> level 0
    for n in incoming:
        levels.setdefault(n, 0)

    # Ensure END node(s) are placed at the bottom-most level
    if levels:
        end_nodes = [name for name in levels.keys() if name.upper() == 'END']
        if end_nodes:
            max_lvl = max(levels.values())
            for en in end_nodes:
                levels[en] = max_lvl + 1

    # Group by level preserving insertion order but sort labels for stability
    level_groups: Dict[int, List[str]] = {}
    for name, lvl in levels.items():
        level_groups.setdefault(lvl, []).append(name)
    for lst in level_groups.values():
        lst.sort()

    sorted_levels = sorted(level_groups.keys())
    max_level_index = len(sorted_levels) - 1
    total_nodes = len(nodes)

    # Base spacing heuristics
    base_vertical_cap = 70
    if total_nodes > 60:
        base_vertical_cap = 40
    elif total_nodes > 40:
        base_vertical_cap = 48
    elif total_nodes > 25:
        base_vertical_cap = 55

    level_spacing = base_vertical_cap
    if max_level_index > 0:
        # Keep vertical span within page-safe bounds while avoiding cramped layouts.
        max_target_span = 680.0
        calculated_spacing = max_target_span / max_level_index if max_level_index else base_vertical_cap
        # Never let spacing collapse below a readable threshold, but honour tighter bounds for huge graphs.
        min_spacing = 34 if total_nodes > 70 else 38 if total_nodes > 45 else 42
        level_spacing = max(min_spacing, min(base_vertical_cap, calculated_spacing))

    # Horizontal spacing bounds (slightly reduced to compress width)
    min_h = 40
    max_h = 100
    if total_nodes > 50:
        max_h = 90
    if total_nodes > 70:
        min_h = 35

    # Offsets (fully centered now; removed left bias)
    center_x_offset = 0
    center_y_offset = 0

    # Order nodes within each level using a barycenter (median) heuristic
    # to preserve left-to-right logical flow and reduce crossings.
    sorted_levels = sorted(level_groups.keys())
    ordered_levels: Dict[int, List[str]] = {}

    def base_sort_key(nm: str):
        nm_upper = nm.upper()
        if nm_upper in start_aliases:
            return (0, -len(outgoing.get(nm, [])), nm)
        elif nm_upper == 'END':
            return (2, 0, nm)
        else:
            return (1, -len(outgoing.get(nm, [])), nm)

    def nearest_prev_level(cur: int) -> Optional[int]:
        prevs = [lv for lv in sorted_levels if lv < cur]
        return prevs[-1] if prevs else None

    if sorted_levels:
        first_level = sorted_levels[0]
        ordered_levels[first_level] = sorted(level_groups[first_level], key=base_sort_key)

    for lvl in sorted_levels[1:]:
        names_list = level_groups[lvl]
        prev_lvl = nearest_prev_level(lvl)
        if prev_lvl is None or prev_lvl not in ordered_levels:
            ordered_levels[lvl] = sorted(names_list, key=base_sort_key)
        else:
            prev_order = ordered_levels[prev_lvl]
            prev_index = {nm: i for i, nm in enumerate(prev_order)}

            def barycenter(nm: str) -> float:
                parents = [p for p in incoming.get(nm, []) if levels.get(p, -1) == prev_lvl]
                if not parents:
                    earlier_parents = [p for p in incoming.get(nm, []) if levels.get(p, 10**9) < lvl]
                    if not earlier_parents:
                        return float('inf')
                    best_level = max(levels[p] for p in earlier_parents)
                    parents = [p for p in earlier_parents if levels[p] == best_level]
                idxs = [prev_index[p] for p in parents if p in prev_index]
                if not idxs:
                    return float('inf')
                return sum(idxs) / len(idxs)

            ordered_levels[lvl] = sorted(
                names_list,
                key=lambda nm: (barycenter(nm), -len(outgoing.get(nm, [])), nm),
            )

    positions: Dict[str, Dict[str, float]] = {}
    for idx, lvl in enumerate(sorted_levels):
        names = ordered_levels.get(lvl, level_groups[lvl])
        # Vertical position: stack centered
        total_vertical_span = max_level_index * level_spacing if max_level_index > 0 else 0
        y = (idx * level_spacing) - (total_vertical_span / 2) + center_y_offset

        count = len(names)
        if count == 1:
            positions[names[0]] = {"x": center_x_offset, "y": y}
            continue

        # Compute spacing
        span = min(max_h, max(min_h, 80 if count == 2 else max_h))
        # Try to compress if many nodes at level
        tentative = span
        if count > 6:
            tentative = max(min_h, min(span, (max_h * 0.8)))
        spacing = min(tentative, max_h)
        total_width = (count - 1) * spacing
        start_x = -total_width / 2 + center_x_offset
        for i, name in enumerate(names):
            positions[name] = {"x": start_x + i * spacing, "y": y}

    # Enforce minimum overall horizontal span (avoid zoom blow-up)
    xs = [p["x"] for p in positions.values()]
    if xs:
        span_x = max(xs) - min(xs)
        # Ensure minimum span for tiny graphs, but also gently normalize very wide graphs.
        if span_x < 120 and len(xs) > 1:
            scale = 120 / span_x if span_x > 0 else 1
            mid_x = (max(xs) + min(xs)) / 2
            for p in positions.values():
                p["x"] = (p["x"] - mid_x) * scale
        elif span_x > 800:  # extremely wide, compress slightly
            scale = 800 / span_x
            mid_x = (max(xs) + min(xs)) / 2
            for p in positions.values():
                p["x"] = mid_x + (p["x"] - mid_x) * scale

    # Apply positions and annotate level for downstream rendering tweaks
    for n in nodes:
        name = n.get("name")
        if name in positions:
            n["fx"] = float(positions[name]["x"])
            n["fy"] = float(positions[name]["y"])
            # Persist relative level index for template (stagger labels)
            n["level"] = int(levels.get(name, 0))

    return graph_data

def generate(graph: GraphDefinition, out_file: str, export_pdf: bool = False):
    svg = from_definition(graph).generate()

    # Apply deterministic workflow layout
    try:
        graph_json = json.loads(svg)
        graph_json = _compute_workflow_layout(graph_json)
        svg = json.dumps(graph_json)
    except Exception:
        # Layout failure should not abort report generation
        pass

    # (Reverted) Removed automatic orientation logic

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates")
        )
    )

    template = env.get_template("template.html.jinja")
    agents = [Agent.model_validate(a, from_attributes=True) for a in graph.agents]
    # Primary tools list (explicit tools attribute)
    tools = [Tool.model_validate(t, from_attributes=True) for t in graph.tools]
    # Fallback: if no explicit tools provided, derive from node list (tool-like node types)
    if not tools:
        try:
            tool_node_types = {NodeType.TOOL, NodeType.CUSTOM_TOOL, NodeType.BASIC}
            derived_tools: list[Tool] = []
            for node in graph.nodes:
                if node.node_type in tool_node_types:
                    vulns = []
                    for v in node.vulnerabilities:
                        try:
                            vulns.append(
                                Vulnerability(
                                    name=v.name,
                                    description=v.description,
                                    security_framework_mapping=v.security_framework_mapping,
                                    remediation=v.remediation,
                                )
                            )
                        except Exception:
                            continue
                    derived_tools.append(
                        Tool(
                            name=node.name,
                            category=str(node.category) if node.category else str(node.node_type),
                            description=node.description or "",
                            vulnerabilities=vulns,
                        )
                    )
            if derived_tools:
                tools = derived_tools
        except Exception:
            # Silent fallback; keep empty if anything unexpected happens
            pass
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
            report_intro=(
                f"This report summarizes the analyzed agentic workflow for project '{graph.name}' using the {graph.framework} framework. "
                f"It identifies {len(agents)} agent(s), {len(tools)} tool(s), and {len([n for n in graph.nodes if n.node_type == NodeType.MCP_SERVER])} MCP server(s). "
                "The sections below provide a deterministic layout of the workflow graph, a consolidated node overview, and any discovered vulnerabilities with recommended mitigations."
            ),
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
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': 1200, 'height': 1600})  # Set explicit viewport for A4-like ratio
                
                # Enable console logging to see debug messages
                page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
                
                report_path = os.path.abspath(out_file).replace('\\', '/')
                # Signal PDF mode so the template applies PDF-specific fitting/bias
                page.goto(f"file:///{report_path}?pdf=true", wait_until="domcontentloaded")
                # Wait for graph container & canvas
                try:
                    page.wait_for_selector('#graph', timeout=12000)
                    page.wait_for_selector('#graph canvas', timeout=12000)
                except Exception:
                    pass
                # Wait for readiness flag if set by template JS
                try:
                    page.wait_for_function("window.__GRAPH_READY__ === true", timeout=6000)
                except Exception:
                    page.wait_for_timeout(1500)
                page.pdf(
                    path=pdf_out,
                    print_background=True,
                    format='A4',
                    margin={'top': '0.5in', 'bottom': '0.5in', 'left': '0.5in', 'right': '0.5in'}
                )
                browser.close()
            print(f"PDF report {pdf_out} generated (via Playwright)")
            return
        except Exception:
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
