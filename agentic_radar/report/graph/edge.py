from pydantic import BaseModel


class Edge(BaseModel):
    source: str
    target: str


class DefaultEdge(Edge):
    def __init__(self, src: str, dst: str, vulnerable: bool = False):
        super().__init__(source=src, target=dst)


class ConditionalEdge(Edge):
    def __init__(self, src: str, dst: str, condition: str, vulnerable: bool = False):
        super().__init__(source=src, target=dst)
