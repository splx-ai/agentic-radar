from enum import Enum
from typing import Dict, List, Optional

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


class VulnerabilityDefinition(BaseModel):
    name: str
    description: str
    security_framework_mapping: Dict[str, str]
    remediation: str


class NodeDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    node_type: NodeType = Field(..., alias="type")
    name: str
    description: Optional[str] = None
    label: Optional[str] = None
    category: Optional[ToolType] = None
    vulnerabilities: List[VulnerabilityDefinition] = Field(default_factory=list)


class EdgeDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    start: str
    end: str
    condition: Optional[str] = None


class GraphDefinition(BaseModel):
    name: str
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    tools: List[NodeDefinition] = Field(default_factory=list)
