import os
import re
import asyncio
from openai import AsyncOpenAI

try:
    from agents import (
        Agent as OriginalAgent,
        Runner,
        set_default_openai_client,
        set_default_openai_api,
        set_tracing_disabled,
    )

    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")

    if base_url:
        try:
            set_default_openai_api("chat_completions")
        except Exception:
            pass

        try:
            set_tracing_disabled(disabled=True)
        except Exception:
            pass

        custom_client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        try:
            set_default_openai_client(custom_client, use_for_tracing=False)
        except Exception:
            try:
                set_default_openai_client(custom_client)
            except Exception:
                pass
except ImportError:
    pass

from ..agent import Agent


class OpenAIAgentsAgent(Agent):
    """OpenAI Agents Adapter for Agentic Radar."""

    def __init__(self, agent: "OriginalAgent") -> None:
        self._agent = agent
        target_model = os.getenv("OPENAI_MODEL", "gemini-3.5-flash-lite")
        if not hasattr(self._agent, "model") or not self._agent.model:
            self._agent.model = target_model

    @property
    def name(self) -> str:
        return self._agent.name

    async def invoke(self, input: str) -> str:
        for attempt in range(5):
            try:
                result = await Runner.run(self._agent, input, max_turns=10)
                return str(result.final_output)
            except Exception as e:
                err_str = str(e)
                # Catch max turns loop and return string output for Oracle grading
                if "Max turns" in err_str:
                    return f"Agent exceeded maximum turns (potential infinite loop or refusal breakdown): {err_str}"
                elif "429" in err_str:
                    wait_match = re.search(r"retry in (\d+(?:\.\d+)?)s", err_str, re.IGNORECASE)
                    wait_time = float(wait_match.group(1)) + 2.0 if wait_match else 55.0
                    print(f"\n[Agent] Rate limit hit on {self.name}. Waiting {int(wait_time)}s for quota window...")
                    await asyncio.sleep(wait_time)
                    continue
                elif "503" in err_str and attempt < 4:
                    print(f"\n[Agent] 503 spike on {self.name}. Retrying in 4s...")
                    await asyncio.sleep(4.0)
                    continue
                raise e

        raise RuntimeError(f"Exceeded retries for agent {self.name}")
