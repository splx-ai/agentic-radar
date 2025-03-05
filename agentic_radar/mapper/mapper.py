import json
from importlib import resources
from typing import List, Literal

from pydantic import BaseModel

from ..graph import GraphDefinition, NodeType, VulnerabilityDefinition


class VulnerabilityMapDefinition(BaseModel):
    type: NodeType
    match: Literal["name", "category"]
    value: str
    vulnerabilities: List[VulnerabilityDefinition]


def load_vulnerabilities() -> List[VulnerabilityMapDefinition]:
    input_file = resources.files(__package__) / "vulnerabilities.json"
    with input_file.open("r") as f:
        data = json.load(f)

    return [VulnerabilityMapDefinition.model_validate(v) for v in data]


def map_vulnerabilities(graph: GraphDefinition):
    """Map vulnerabilities to nodes and tools in the graph"""

    vulnerabilities = load_vulnerabilities()

    # Map vulnerabilities to nodes
    for node in graph.nodes:
        for vulnerability in vulnerabilities:
            if vulnerability.type == node.node_type:
                if vulnerability.match == "name" and vulnerability.value == node.name:
                    node.vulnerabilities.extend(vulnerability.vulnerabilities)
                elif (
                    vulnerability.match == "category"
                    and vulnerability.value == node.category.value
                ):
                    node.vulnerabilities.extend(vulnerability.vulnerabilities)

    # Map vulnerabilities to tools
    for tool in graph.tools:
        for vulnerability in vulnerabilities:
            if vulnerability.type == tool.node_type:
                if vulnerability.match == "name" and vulnerability.value == tool.name:
                    tool.vulnerabilities.extend(vulnerability.vulnerabilities)
                elif (
                    vulnerability.match == "category"
                    and vulnerability.value == tool.category.value
                ):
                    tool.vulnerabilities.extend(vulnerability.vulnerabilities)
