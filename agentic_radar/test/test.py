from abc import ABC, abstractmethod
from dataclasses import dataclass

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


@dataclass
class Test(ABC):
    """
    Base class for tests.
    Tests are used to test individual agents.
    """

    name: str

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


@dataclass
class OracleBasedTest(Test):
    """
    Test evaluated by an oracle LLM.
    """

    name: str
    input: str
    success_condition: str

    async def run(self, agent: Agent) -> TestResult:
        input = self.input
        output = await agent.invoke(input)
        oracle_evaluation = await evaluate_test(
            test_explanation=self.success_condition,
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
