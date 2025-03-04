from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    AGENT = "Agent"
    BASIC = "Basic"
    TOOL = "Tool"
    CUSTOM_TOOL = "CustomTool"


class NodeCategory(str, Enum):
    LLM = "LLM"
    CODE_INTERPRETER = "Code Interpreter"
    WEB_SEARCH = "Web Search"
    DOCUMENT_LOADER = "Document Loader"
    # Others TBD based on the vulnerability mapping


class Node(BaseModel):
    type: NodeType = Field(..., description="Type of the node")
    name: str = Field(..., description="Name of the node")
    label: str = Field(..., description="Label of the node")
    category: Optional[NodeCategory] = Field(
        default=None, description="Category of the tool (only for Tool nodes)"
    )


class Edge(BaseModel):
    start_node: str = Field(..., description="Label of the starting node")
    end_node: str = Field(..., description="Label of the end node")
    condition: Optional[str] = Field(
        default=None, description="Optional condition for the edge"
    )
