from typing import List

from pydantic import BaseModel

from agentic_radar.report.graph.edge import Edge
from agentic_radar.report.graph.node import Node


class Graph(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []

    def generate(self) -> str:
        return self.model_dump_json()
