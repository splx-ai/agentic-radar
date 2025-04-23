import ast
from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, PrivateAttr


class Tool(BaseModel):
    name: str
    custom: bool
    description: Optional[str] = None


class MCPServerType(str, Enum):
    STDIO = "stdio"
    SSE = "sse"


class MCPServerInfo(BaseModel):
    var: str
    name: Optional[str] = None
    type: MCPServerType
    params: dict[str, str] = {}


class Guardrail(BaseModel):
    name: str
    placement: Literal['input', 'output']
    uses_agent: bool
    guardrail_function_name: str
    _guardrail_function_def: Optional[Union[ast.FunctionDef, ast.AsyncFunctionDef]] = PrivateAttr(default=None)
    agent_instructions: Optional[str] = None
    agent_name: Optional[str] = None


class AgentVulnerability(BaseModel):
    name: str
    mitigation_level: Literal["None", "Partial", "Full"]
    guardrail_explanation: str
    instruction_explanation: str


class Agent(BaseModel):
    name: str
    tools: list[Tool]
    handoffs: list[str]
    instructions: Optional[str] = None
    model: Optional[str] = None
    mcp_servers: list[MCPServerInfo] = []
    is_guardrail: bool = False
    guardrails: dict[str, list[str]] = Field(default_factory=dict)
    vulnerabilities: list[AgentVulnerability] = Field(default_factory=list)
