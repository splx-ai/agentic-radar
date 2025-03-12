from pydantic import BaseModel, Field

class CrewAITool(BaseModel):
    name: str = Field(..., description="Name of the tool")
    custom: bool = Field(False, description="Indicator of whether it is a custom or predefined tool")
    description: str = Field("", description="Short description of what the tool does")