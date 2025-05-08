import functools
import sys

from ..agent_adapters import OpenAIAgentsAgent
from ..test import Test
from .base_launcher import BaseLauncher


class OpenAIAgentsLauncher(BaseLauncher):
    """
    This class is responsible for launching the OpenAI Agents workflow and collecting agents inside it.
    It patches the Agent constructor method to register the agents and run methods to terminate the workflow early.
    """

    def __init__(
        self, entrypoint_script: str, extra_args: list[str], tests: list[Test]
    ):
        super().__init__(entrypoint_script, extra_args, tests)

    def _patch_targets(self) -> None:
        try:
            import agents

            if hasattr(agents, "Agent") and hasattr(agents.Agent, "__init__"):
                original_agent_init = agents.Agent.__init__
                original_runner_run = agents.Runner.run
                original_runner_run_streamed = agents.Runner.run_streamed
            else:
                raise ValueError(
                    "[Launcher] ERROR: 'agents.Agent.__init__' not found. Patch not applied."
                )
        except ImportError:
            raise ImportError(
                "[Launcher] ERROR: 'agents' module not found. Ensure the OpenAI Agents library is installed."
            )
        except Exception as e:
            raise RuntimeError(f"[Launcher] ERROR during patching setup: {e}")

        @functools.wraps(original_agent_init)
        def patched_agent_init(agent_self, *args, **kwargs):
            try:
                if original_agent_init is None:
                    raise RuntimeError(
                        "[Launcher] ERROR: Original __init__ not available!"
                    )

                original_agent_init(agent_self, *args, **kwargs)

            except Exception as e:
                print(
                    f"[Launcher] ERROR during original __init__ for agent {kwargs.get('name', args[0] if args else 'Unknown Agent')}: {e}"
                )
                raise

            # Register the agent instance
            self._register_agent(OpenAIAgentsAgent(agent_self))

        @functools.wraps(original_runner_run)
        async def patched_runner_run(runner_self, *args, **kwargs):
            print(f"[Launcher] Runner.run() called with args: {args}, kwargs: {kwargs}")
            print("[Launcher] Terminating workflow early.")
            sys.exit(0)

        @functools.wraps(original_runner_run_streamed)
        def patched_run_streamed(runner_self, *args, **kwargs):
            print(
                f"[Launcher] Runner.run_streamed() called with args: {args}, kwargs: {kwargs}"
            )
            print("[Launcher] Terminating workflow early.")
            sys.exit(0)

        # Apply the patches
        agents.Agent.__init__ = patched_agent_init  # type: ignore[assignment]
        agents.Runner.run = patched_runner_run  # type: ignore[assignment]
        agents.Runner.run_streamed = patched_run_streamed  # type: ignore[assignment]

        # Remember the original methods for later restoration
        self._original_agent_init = original_agent_init
        self._original_runner_run = original_runner_run
        self._original_runner_run_streamed = original_runner_run_streamed

    def _revert_patches(self) -> None:
        try:
            import agents

            # Revert the patches
            agents.Agent.__init__ = self._original_agent_init  # type: ignore[assignment]
            agents.Runner.run = self._original_runner_run  # type: ignore[assignment]
            agents.Runner.run_streamed = self._original_runner_run_streamed  # type: ignore[assignment]

        except ImportError:
            print("[Launcher] ERROR: 'agents' module not found. Cannot revert patches.")
        except Exception as e:
            print(f"[Launcher] ERROR during patch reverting: {e}")
