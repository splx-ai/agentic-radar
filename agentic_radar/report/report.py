import datetime
import os
import re
from typing import Dict, List, Optional

import jinja2
from pydantic import BaseModel, Field

from agentic_radar import __version__

from ..graph import NodeType
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


class ReportData(BaseModel):
    project_name: str
    framework: str
    timestamp: str
    graph: str

    count: Dict[str, int]

    tools: List[Tool]
    scanner_version: str


def generate(graph: GraphDefinition, out_file: str):
    svg = from_definition(graph).generate()

    # remove xml definition, and put relative width and height
    svg_lines = svg.splitlines()[1:]
    svg_lines[0] = re.sub(r'width="(.*?)"', 'width="100%"', svg_lines[0])
    svg_lines[0] = re.sub(
        r'height="(.*?)"', 'height="100%" preserveAspectRatio="xMidYMin"', svg_lines[0]
    )
    svg = "\n".join(svg_lines)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates")
        )
    )

    template = env.get_template("template.html.jinja")
    tools = [Tool.model_validate(t, from_attributes=True) for t in graph.tools]
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
            tools=tools,
            scanner_version=__version__,
        ).model_dump()
    ).dump(out_file)
