from abc import ABC, abstractmethod

from pydantic import BaseModel

from .agent import Agent
from .oracle import evaluate_probe


class ProbeResult(BaseModel):
    agent_name: str
    probe_name: str
    input: str
    output: str
    test_passed: bool
    explanation: str


class Probe(ABC):
    """
    Base class for probes.
    Probes are used to test individual agents.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the probe.
        """
        pass

    @abstractmethod
    async def run(self, agent: Agent) -> ProbeResult:
        """
        Run the probe on the given agent.

        Args:
            agent (Agent): The agent to probe.

        Returns:
            ProbeResult: The result of the probe.
        """
        pass


class OracleBasedProbe(Probe, ABC):
    """
    Abstract base class for probes evaluated by an oracle LLM.
    """

    @property
    @abstractmethod
    def _input(self) -> str:
        pass

    @property
    @abstractmethod
    def _success_condition(self) -> str:
        pass

    async def run(self, agent: Agent) -> ProbeResult:
        input = self._input
        output = await agent.invoke(input)
        oracle_evaluation = await evaluate_probe(
            probe_explanation=self._success_condition,
            input_text=input,
            output_text=output,
        )
        return ProbeResult(
            agent_name=agent.name,
            probe_name=self.name,
            input=input,
            output=output,
            test_passed=not oracle_evaluation.attack_succeeded,
            explanation=oracle_evaluation.explanation,
        )
