from typing import Optional

from pydantic import BaseModel


class Tool(BaseModel):
    name: str
    custom: bool
    description: Optional[str] = None

class Agent(BaseModel):
    name: str
    tools: list[str]
    handoffs: list[str]

    
