from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NodeType(StrEnum):
    AGENT = "agent"
    BASIC = "basic"
    TOOL = "tool"
    CUSTOM_TOOL = "custom_tool"
    DEFAULT = "default"


class ToolType(StrEnum):
    WEB_SEARCH = "web_search"
    LLM = "llm"
    CODE_INTERPRETER = "code_interpreter"
    DOCUMENT_LOADER = "document_loader"
    DEFAULT = "default"


class NodeDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    node_type: NodeType = Field(..., alias="type")
    name: str
    label: Optional[str] = None
    category: Optional[ToolType] = None


class EdgeDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    start: str
    end: str
    condition: Optional[str] = None


class GraphDefinition(BaseModel):
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
