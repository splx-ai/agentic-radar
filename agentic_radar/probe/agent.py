from abc import ABC, abstractmethod


class Agent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the agent."""
        pass

    @abstractmethod
    async def invoke(self, input: str) -> str:
        """
        Invoke the agent with the given input.

        Args:
            input: The input to send to the agent.

        Returns:
            The agent's response.
        """
        pass
