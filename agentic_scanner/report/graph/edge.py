import pydot


class Edge(pydot.Edge):
    def __init__(self, src: str, dst: str, vulnerable: bool = False):
        super().__init__(src, dst, color="#E20E14" if vulnerable else "#1ED044")


class ConditionalEdge(pydot.Edge):
    def __init__(self, src: str, dst: str, condition: str, vulnerable: bool = False):
        super().__init__(
            src, dst, style="dashed", color="#E20E14" if vulnerable else "#1ED044"
        )
        # self.set_label(condition)  # type: ignore
