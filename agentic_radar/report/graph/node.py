import base64
from typing import Optional

import importlib_resources as resources
from pydantic import BaseModel

from ...graph import NodeType, ToolType


def _image_to_data_url(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
        return "data:image/svg+xml;base64," + base64.encodebytes(data).decode("utf-8")


class Node(BaseModel):
    name: str
    label: str
    image: str
    node_type: str
    tool_category: Optional[str] = None


class AgentNode(Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name=name,
            label=label,
            image=_image_to_data_url(
                str(resources.files(__package__) / "assets" / "agent.svg")
            ),
            node_type=str(NodeType.AGENT),
        )


class BasicNode(Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name=name,
            label=label,
            image=_image_to_data_url(
                str(resources.files(__package__) / "assets" / "basic.svg")
            ),
            node_type=str(NodeType.BASIC),
        )


class ToolNode(Node):
    def __init__(self, name: str, label: str, tool_type: Optional[ToolType] = None):
        ttype = str(tool_type or ToolType.DEFAULT)
        super().__init__(
            name=name,
            label=label,
            image=_image_to_data_url(
                str(resources.files(__package__) / "assets" / "tools" / f"{ttype}.svg")
            ),
            node_type=str(NodeType.TOOL),
            tool_category=ttype,
        )


class CustomToolNode(Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name=name,
            label=label,
            image=_image_to_data_url(
                str(resources.files(__package__) / "assets" / "custom_tool.svg")
            ),
            node_type=str(NodeType.CUSTOM_TOOL),
        )


class MCPServerNode(Node):
    def __init__(self, name: str, label: str):
        super().__init__(
            name=name,
            label=label,
            image=_image_to_data_url(
                str(resources.files(__package__) / "assets" / "mcp_server.svg")
            ),
            node_type=str(NodeType.MCP_SERVER),
        )
