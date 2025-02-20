from typing import Optional

import pydot

from ..graph import ToolType


class AgentNode(pydot.Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name,
            label=label,
            shape="box",
            color="black",
            fillcolor="burlywood4",
            labelloc="b",
            style="rounded,bold,filled",
        )


class BasicNode(pydot.Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name,
            label=label,
            shape="box",
            color="black",
            fillcolor="dodgerblue3",
            labelloc="b",
            style="rounded,bold,filled",
        )


class ToolNode(pydot.Node):
    def __init__(self, name: str, label: str, tool_type: Optional[ToolType] = None):
        # TODO: depending on tool type, set shape, color, icon...
        super().__init__(
            name,
            label=label,
            shape="box",
            color="black",
            style="rounded,bold",
            labelloc="b",
        )


class CustomToolNode(pydot.Node):
    def __init__(self, name: str, label: str):
        super().__init__(name, label=label, shape="ellipse", labelloc="b")
