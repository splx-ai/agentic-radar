from typing import Optional

from pydantic import BaseModel

from .tool import CrewAITool


class PartialCrewAIAgent(BaseModel):
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    tools: Optional[list[CrewAITool]] = None
    llm: Optional[str] = None
    system_template: Optional[str] = None
    prompt_template: Optional[str] = None
    response_template: Optional[str] = None
    use_system_prompt: Optional[bool] = True


class CrewAIAgent(BaseModel):
    role: str
    goal: str
    backstory: str
    tools: list[CrewAITool] = []
    llm: str = "gpt-4"
    use_system_prompt: bool = True
    system_template: Optional[str] = None
    prompt_template: Optional[str] = None
    response_template: Optional[str] = None

    @classmethod
    def from_partial_agent(cls, partial_agent: PartialCrewAIAgent) -> "CrewAIAgent":
        if partial_agent.role is None:
            raise ValueError("Role must be provided")
        if partial_agent.goal is None:
            raise ValueError("Goal must be provided")
        if partial_agent.backstory is None:
            raise ValueError("Backstory must be provided")

        return cls(
            role=partial_agent.role,
            goal=partial_agent.goal,
            backstory=partial_agent.backstory,
            tools=partial_agent.tools or [],
            llm=partial_agent.llm or "gpt-4",
            system_template=partial_agent.system_template,
            prompt_template=partial_agent.prompt_template,
            response_template=partial_agent.response_template,
            use_system_prompt=partial_agent.use_system_prompt
            if partial_agent.use_system_prompt is not None
            else True,
        )

    @classmethod
    def from_partial_agents(
        cls,
        code_partial_agent: PartialCrewAIAgent,
        yaml_partial_agent: PartialCrewAIAgent,
    ) -> "CrewAIAgent":
        role = code_partial_agent.role or yaml_partial_agent.role
        goal = code_partial_agent.goal or yaml_partial_agent.goal
        backstory = code_partial_agent.backstory or yaml_partial_agent.backstory
        if role is None:
            raise ValueError("Role must be provided, either in code or YAML")
        if goal is None:
            raise ValueError("Goal must be provided, either in code or YAML")
        if backstory is None:
            raise ValueError("Backstory must be provided, either in code or YAML")

        return cls(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=code_partial_agent.tools or yaml_partial_agent.tools or [],
            llm=code_partial_agent.llm or yaml_partial_agent.llm or "gpt-4",
            system_template=code_partial_agent.system_template
            or yaml_partial_agent.system_template,
            prompt_template=code_partial_agent.prompt_template
            or yaml_partial_agent.prompt_template,
            response_template=code_partial_agent.response_template
            or yaml_partial_agent.response_template,
            use_system_prompt=(
                code_partial_agent.use_system_prompt
                if code_partial_agent.use_system_prompt is not None
                else (
                    yaml_partial_agent.use_system_prompt
                    if yaml_partial_agent.use_system_prompt is not None
                    else True
                )
            ),
        )
