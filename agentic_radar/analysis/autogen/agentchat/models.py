from enum import Enum

from pydantic import BaseModel


class FunctionDefinition(BaseModel):
    name: str
    description: str


class ModelClient(BaseModel):
    name: str
    model: str


class FunctionTool(BaseModel):
    name: str
    description: str


class Agent(BaseModel):
    name: str
    tools: list[FunctionTool]
    llm: str = ""
    system_prompt: str = ""
    handoffs: list[str] = []


class TeamType(str, Enum):
    ROUND_ROBIN_GROUP_CHAT = "round_robin_group_chat"
    SELECTOR_GROUP_CHAT = "selector_group_chat"
    MAGENTIC_ONE_GROUP_CHAT = "magentic_one_group_chat"
    SWARM = "swarm"


class Team(BaseModel):
    type: TeamType
    members: list[Agent]
