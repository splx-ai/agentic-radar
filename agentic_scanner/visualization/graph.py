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
            outputorder="edgesfirst",
            sep="+60",
            labelloc="b",
            normalize=True,
        )
        self.set_node_defaults(fontsize=16, forcelabels=True, fontname="Inter")
        self.set_edge_defaults(fontsize=16, forcelabels=True, fontname="Inter")

        for node in nodes:
            self.add_node(node)

        for edge in edges:
            self.add_edge(edge)

    def generate(self, output_file: str):
        subprocess.run(
            ["dot", "-Tsvg:cairo", "-o", output_file],
            input=str(self).encode(),
            check=True,
        )
