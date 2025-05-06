from abc import ABC, abstractmethod

from pydantic import BaseModel

from .agent import Agent
from .oracle import evaluate_test


class TestResult(BaseModel):
    agent_name: str
    test_name: str
    input: str
    output: str
    test_passed: bool
    explanation: str


class Test(ABC):
    """
    Base class for tests.
    Tests are used to test individual agents.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the test.
        """
        pass

    @abstractmethod
    async def run(self, agent: Agent) -> TestResult:
        """
        Run the test on the given agent.

        Args:
            agent (Agent): The agent to test.

        Returns:
            TestResult: The result of the test.
        """
        pass


class OracleBasedTest(Test, ABC):
    """
    Abstract base class for tests evaluated by an oracle LLM.
    """

    @property
    @abstractmethod
    def _input(self) -> str:
        pass

    @property
    @abstractmethod
    def _success_condition(self) -> str:
        pass

    async def run(self, agent: Agent) -> TestResult:
        input = self._input
        output = await agent.invoke(input)
        oracle_evaluation = await evaluate_test(
            test_explanation=self._success_condition,
            input_text=input,
            output_text=output,
        )
        return TestResult(
            agent_name=agent.name,
            test_name=self.name,
            input=input,
            output=output,
            test_passed=not oracle_evaluation.attack_succeeded,
            explanation=oracle_evaluation.explanation,
        )
