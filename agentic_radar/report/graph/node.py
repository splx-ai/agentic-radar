import base64
from importlib import resources
from typing import Optional

from pydantic import BaseModel

from ...graph import ToolType


def _load_image(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
        return "data:image/svg+xml;base64," + base64.encodebytes(data).decode("utf-8")


class Node(BaseModel):
    name: str
    label: str
    image: str


class AgentNode(Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name=name,
            label=label,
            image=_load_image(
                str(resources.files(__package__) / "assets" / "agent.svg")
            ),
        )


class BasicNode(Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name=name,
            label=label,
            image=_load_image(
                str(resources.files(__package__) / "assets" / "basic.svg")
            ),
        )


class ToolNode(Node):
    def __init__(self, name: str, label: str, tool_type: Optional[ToolType] = None):
        ttype = str(tool_type or ToolType.DEFAULT)
        super().__init__(
            name=name,
            label=label,
            image=_load_image(
                str(resources.files(__package__) / "assets" / "tools" / f"{ttype}.svg")
            ),
        )


class CustomToolNode(Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name=name,
            label=label,
            image=_load_image(
                str(resources.files(__package__) / "assets" / "custom_tool.svg")
            ),
        )
