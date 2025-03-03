import datetime
import os
import re
from typing import Dict, List

import jinja2
from pydantic import BaseModel, Field

from agentic_scanner.graph import NodeType

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
    description: str
    vulnerabilities: List[Vulnerability] = Field(default_factory=list)

class ReportData(BaseModel):
    project_name: str
    timestamp: str
    graph: str

    count: Dict[str, int]

    tools: List[Tool]


def generate(graph: GraphDefinition, out_file: str):
    svg = from_definition(graph).generate()

    # remove xml definition, and put relative width and height
    svg_lines = svg.splitlines()[1:]
    svg_lines[0] = re.sub(r'width="(.*?)"', 'width="100%"', svg_lines[0])
    svg_lines[0] = re.sub(r'height="(.*?)"', 'height="100%"', svg_lines[0])
    svg = "\n".join(svg_lines)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates")
        )
    )

    template = env.get_template("template.html.jinja")

    template.stream(**ReportData(
        project_name=graph.name,
        timestamp=datetime.datetime.now().strftime("%x %X"),
        graph=svg,
        count={
            "tools": len(graph.tools),
            "agents": len([x for x in graph.nodes if x.node_type == NodeType.AGENT]),
            "vulnerability": 0, #TODO: map node vulnerabilities
            },
        tools=[
            #TODO: map node vulnerabilities
            Tool(
                name="create_issue",
                category="Code interpreter",
                description="Tool description",
                vulnerabilities=[
                    Vulnerability(
                        name= "Improper Output Handling",
                        description="Generated",
                        security_framework_mapping={
                            "CVE": "blabla",
                            "OWASP LLM TOP 10": "blabla"
                            },
                        remediation="Remediate placholder"
                        ),
                    Vulnerability(
                        name= "Improper Output Handling 2",
                        description="Generated",
                        security_framework_mapping={
                            "CVE": "blabla",
                            "OWASP LLM TOP 10": "blabla"
                            },
                        remediation="Placeholder"
                        ),
                    ]
                ),
            Tool(
                name="create_issue 2",
                category="Code interpreter",
                description="Tool description",
                vulnerabilities=[
                    Vulnerability(
                        name= "Improper Output Handling",
                        description="Generated",
                        security_framework_mapping={
                            "CVE": '<span style="color: black; font-size: 10px; font-family: Inter; font-weight: 400; text-decoration: underline; line-height: 15px; word-wrap: break-word">CVE-2023-44467</span>',
                            "OWASP LLM TOP 10": "blabla"
                            },
                        remediation="Remediate placholder"
                        ),
                    Vulnerability(
                        name= "Improper Output Handling 2",
                        description="Generated",
                        security_framework_mapping={
                            "CVE": "blabla",
                            "OWASP LLM TOP 10": "blabla"
                            },
                        remediation="Placeholder"
                        ),
                    ]
                ),
            ]
        ).model_dump()).dump(out_file)
