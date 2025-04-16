from enum import Enum
from typing import Optional

from pydantic import BaseModel


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


class Agent(BaseModel):
    name: str
    tools: list[Tool]
    handoffs: list[str]
    instructions: Optional[str] = None
    model: Optional[str] = None
    mcp_servers: list[MCPServerInfo] = []
