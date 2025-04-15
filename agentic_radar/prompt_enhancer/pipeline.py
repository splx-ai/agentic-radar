from abc import ABC, abstractmethod


class PromptEnhancingStep(ABC):
    @abstractmethod
    def enhance(self, system_prompt: str) -> str:
        pass


class PromptEnhancingPipeline:
    def __init__(self, steps: list[PromptEnhancingStep]) -> None:
        self._steps: list[PromptEnhancingStep] = steps

    def run(self, system_prompt: str) -> str:
        for step in self._steps:
            system_prompt = step.enhance(system_prompt)

        return system_prompt
