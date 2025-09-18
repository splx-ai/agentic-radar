import json
from typing import List

from pydantic import BaseModel

from agentic_radar.report.graph.edge import Edge
from agentic_radar.report.graph.node import Node


class Graph(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []

    def generate(self) -> str:
        # ForceGraph.js expects "links" not "edges"
        data = self.model_dump()
        data["links"] = data.pop("edges")
        return json.dumps(data)
