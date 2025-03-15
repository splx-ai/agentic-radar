from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class N8nNode(BaseModel):
    type: str = Field(..., description="Type of the node")
    name: str = Field(..., description="Name of the node")
    id: str = Field(..., description="Id of the node")


class N8nConnection(BaseModel):
    start_node: str = Field(..., description="Id of the starting node")
    end_node: str = Field(..., description="Id of the end node")
    condition: Optional[str] = Field(
        default=None, description="Optional condition for the edge"
    )