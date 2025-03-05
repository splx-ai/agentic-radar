import os
from pprint import pprint

from agentic_radar.graph import GraphDefinition
from agentic_radar.analysis.analyze import Analyzer
from agentic_radar.analysis.crewai.module_parser import CrewAIModuleParser
from agentic_radar.analysis.crewai.graph_converter import convert_graph
from agentic_radar.analysis.crewai.models import CrewAIGraph


class CrewAIAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def _parse_folder(self, folder_path: str, parser: CrewAIModuleParser):
        """
        Parse all Python files in the given folder and its subfolders.
        Each parse method call parses one Python module and merges its CrewAIGraph representation with the accumulated representation stored in CrewAIModuleParser.
        """
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    parser.parse(file_path)

    def analyze(self, root_directory: str) -> GraphDefinition:
        """Analyze the CrewAI codebase and return the graph."""

        crewai_graph = CrewAIGraph(name="CrewAI Graph")
        crewai_parser = CrewAIModuleParser(crewai_graph)
        self._parse_folder(root_directory, crewai_parser)
        graph = convert_graph(crewai_graph)

        return graph

if __name__ == "__main__":
    analyzer = CrewAIAnalyzer()
    graph = analyzer.analyze("../crewai-examples/crewAI-examples/surprise_trip")
    pprint(graph.model_dump(), sort_dicts=False)