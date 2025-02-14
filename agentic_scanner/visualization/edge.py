import pydot


class Edge(pydot.Edge):
    def __init__(self, src: str, dst: str):
        super().__init__(src, dst)


class ConditionalEdge(pydot.Edge):
    def __init__(self, src: str, dst: str, condition: str):
        super().__init__(src, dst, style="dashed")
        self.set_label(condition) # type: ignore
