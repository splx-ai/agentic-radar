import abc
from typing import List, Union

from ..graph import GraphDefinition


class Analyzer(abc.ABC):
    def analyze(self, root_directory: str) -> Union[GraphDefinition, List[GraphDefinition]]:
        raise NotImplementedError()
