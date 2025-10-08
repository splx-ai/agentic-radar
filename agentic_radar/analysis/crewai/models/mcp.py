from pydantic import BaseModel


class CrewAIMCPServer(BaseModel):
    name: str
    params: dict[str, str] = {}
