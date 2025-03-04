import abc

from ..graph import GraphDefinition


class Analyzer(abc.ABC):
    def analyze(self, root_directory: str) -> GraphDefinition:
        raise NotImplementedError()
