import asyncio
import runpy
import sys
from abc import ABC, abstractmethod

from ..agent import Agent
from ..rich import display_test_results
from ..test import Test


class BaseLauncher(ABC):
    """
    Base class for launching tests.
    """

    def __init__(
        self, entrypoint_script: str, extra_args: list[str], tests: list[Test]
    ):
        self.entrypoint_script = entrypoint_script
        self.extra_args = extra_args
        self.tests = tests
        self._collected_agents: list[Agent] = []

    @abstractmethod
    def _patch_targets(self) -> None:
        """
        Patch targets. The patched function MUST call self._register_agent
        with the initialized instance after the original method runs.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @abstractmethod
    def _revert_patches(self) -> None:
        raise NotImplementedError("Subclasses should implement this method.")

    def _register_agent(self, agent_instance: Agent) -> None:
        """
        Callback method to be invoked by the patched function(s)
        after an agent instance is successfully initialized.
        Stores the instance for later testing.
        """
        agent_name = getattr(agent_instance, "name", "UnknownAgent")
        print(
            f"[Launcher] Registered agent instance: {agent_name} ({type(agent_instance).__name__})"
        )
        self._collected_agents.append(agent_instance)

    def _start_workflow(self) -> None:
        original_sys_argv = list(sys.argv)
        exit_code = 0
        try:
            sys.argv[1:] = self.extra_args
            print(
                f"[Launcher] Starting workflow by running script: {self.entrypoint_script}"
            )
            runpy.run_path(self.entrypoint_script, run_name="__main__")
            print("[Launcher] Workflow run finished.")
        except SystemExit as e:
            print(f"[Launcher] Workflow called sys.exit({e.code})")
            if not e.code:
                print("[Launcher] No exit code provided. Defaulting to 0.")
                exit_code = 0
            else:
                exit_code = int(e.code)
        except Exception as e:
            print(f"[Launcher] Error during workflow execution: {e}")
            exit_code = 1
        finally:
            sys.argv = original_sys_argv

        print(
            f"[Launcher] Workflow finished with exit code: {exit_code}. Found {len(self._collected_agents)} agents."
        )

    async def _run_tests(self):
        """
        Run all tests on the collected agents.
        """
        results = []
        for agent in self._collected_agents:
            print(f"[Launcher] Running tests on agent: {agent.name}")
            for test in self.tests:
                print(f"[Launcher] Running test: {test.name}")
                result = await test.run(agent)
                results.append(result)
            print(f"[Launcher] Finished running tests on agent: {agent.name}")
        print("[Launcher] All tests finished.")
        print("[Launcher] Displaying test results:")
        display_test_results(results)

    def launch(self):
        self._patch_targets()
        print("[Launcher] Targets patched.")
        self._start_workflow()
        self._revert_patches()
        print("[Launcher] Reverted patches.")

        try:
            try:
                loop = asyncio.get_running_loop()
                print("[Launcher] Using existing event loop.")
                loop.run_until_complete(self._run_tests())
            except RuntimeError:
                print("[Launcher] No event loop running. Starting one.")
                asyncio.run(self._run_tests())
        except Exception as e:
            print(f"[Launcher] Error during launch: {e}")
            self._revert_patches()
            print("[Launcher] Reverted patches.")
