try:
    from agents import Agent as OriginalAgent
    from agents import Runner
except ImportError:
    pass

from ..agent import Agent


class OpenAIAgentsAgent(Agent):
    """OpenAI Agents Adapter for Agentic Radar."""

    def __init__(self, agent: "OriginalAgent") -> None:
        """
        Initialize the OpenAI Agents adapter.

        Args:
            agent: The OpenAI Agents agent instance.
        """
        self._agent = agent

    @property
    def name(self) -> str:
        return self._agent.name

    async def invoke(self, input: str) -> str:
        result = await Runner.run(self._agent, input)
        return str(result.final_output)
