from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NodeType(Enum):
    AGENT = "agent"
    BASIC = "basic"
    TOOL = "tool"
    CUSTOM_TOOL = "custom_tool"
    DEFAULT = "default"

    def __str__(self) -> str:
        return self.value


class ToolType(Enum):
    WEB_SEARCH = "web_search"
    LLM = "llm"
    CODE_INTERPRETER = "code_interpreter"
    DOCUMENT_LOADER = "document_loader"
    DEFAULT = "default"

    def __str__(self) -> str:
        return self.value


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
    name: str
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
