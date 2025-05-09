from abc import ABC, abstractmethod


class PromptHardeningStep(ABC):
    @abstractmethod
    def harden(self, system_prompt: str) -> str:
        pass


class PromptHardeningPipeline:
    def __init__(self, steps: list[PromptHardeningStep]) -> None:
        self._steps: list[PromptHardeningStep] = steps

    def run(self, system_prompt: str) -> str:
        for step in self._steps:
            system_prompt = step.harden(system_prompt)

        return system_prompt
