import subprocess
from typing import List

import pydot


class Graph(pydot.Dot):
    def __init__(self, nodes: List[pydot.Node], edges: List[pydot.Edge]):
        super().__init__(
            graph_type="digraph",
            fontname="calibre",
            fontsize="1.0",
            layout="sfdp",
            overlap="prism1000",
            pack=True,
        )

        for node in nodes:
            self.add_node(node)

        for edge in edges:
            self.add_edge(edge)

    def generate(self, output_file: str):
        subprocess.run(
            ["dot", "-Tsvg", "-o", output_file], input=str(self).encode(), check=True
        )
