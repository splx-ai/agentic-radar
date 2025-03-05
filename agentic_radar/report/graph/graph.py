import subprocess
from typing import List

import pydot


class Graph(pydot.Dot):
    def __init__(self, nodes: List[pydot.Node], edges: List[pydot.Edge]):
        super().__init__(
            graph_type="digraph",
            fontname="Inter",
            layout="neato",
            overlap="prism",
            mode="sgd",
            outputorder="nodesfirst",
            sep="+50",
            labelloc="b",
            normalize=True,
        )
        self.set_node_defaults(fontsize=20, forcelabels=True, fontname="Inter")
        self.set_edge_defaults(fontsize=20, forcelabels=True, fontname="Inter")

        for node in nodes:
            self.add_node(node)

        for edge in edges:
            self.add_edge(edge)

    def generate(self) -> str:
        return subprocess.check_output(
            ["dot", "-Tsvg:cairo"],
            input=str(self).encode(),
        ).decode("utf-8")
