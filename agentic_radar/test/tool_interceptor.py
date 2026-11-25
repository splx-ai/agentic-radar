"""
Mock tool interceptor for indirect prompt poisoning tests.

Hooks into target agents (such as OpenAI Agents SDK ``FunctionTool`` instances
or generic Python tool callables) to return poisoned external tool outputs from
``indirect_payloads.yaml`` instead of calling real external services.  When a
target agent has no matching tools or does not invoke a tool during a run, a
context-injection hook supplies the simulated untrusted tool output so indirect
injection testing still executes reliably.
"""

from __future__ import annotations

import inspect
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

DEFAULT_INDIRECT_PAYLOADS_PATH = Path(__file__).parent / "indirect_payloads.yaml"


class IndirectPayload(BaseModel):
    """Schema for a single indirect tool poisoning test case."""

    id: str = Field(description="Unique identifier for the indirect poisoning test case")
    name: str = Field(description="Human-readable display name for the test case")
    benign_user_prompt: str = Field(
        description="Legitimate user prompt sent to trigger the agent workflow"
    )
    target_tool: str = Field(
        default="*",
        description="Specific tool name to intercept, or '*' to intercept any tool call",
    )
    poisoned_tool_output: str = Field(
        description="Simulated external tool output containing a hidden adversarial instruction"
    )
    expected_safe_behavior: str = Field(
        description="Criteria describing how a safe agent should behave"
    )


def load_indirect_payloads(
    payloads_path: Optional[Path] = None,
) -> list[IndirectPayload]:
    """Load and validate indirect poisoning payloads from a YAML file.

    Args:
        payloads_path: Optional path to a YAML file. Defaults to the bundled
            ``indirect_payloads.yaml``.

    Returns:
        List of validated :class:`IndirectPayload` objects.

    Raises:
        ValueError: If the YAML file is empty, malformed, or defines no payloads.
    """
    path = payloads_path or DEFAULT_INDIRECT_PAYLOADS_PATH
    with path.open("r", encoding="utf-8") as fh:
        raw_data = yaml.safe_load(fh)

    if isinstance(raw_data, dict):
        entries = raw_data.get("payloads")
        if entries is None:
            raise ValueError(
                f"Indirect payloads YAML '{path}' must contain a 'payloads' list."
            )
    elif isinstance(raw_data, list):
        entries = raw_data
    else:
        raise ValueError(
            f"Indirect payloads YAML '{path}' must be a mapping or list of payloads."
        )

    if not entries:
        raise ValueError(f"Indirect payloads YAML '{path}' contains no test cases.")

    return [IndirectPayload.model_validate(entry) for entry in entries]


class ToolInterceptor:
    """Lightweight interceptor that replaces tool outputs with poisoned payloads."""

    def __init__(self, payload: IndirectPayload) -> None:
        self.payload = payload
        self.triggered: bool = False
        self.intercepted_tools: list[str] = []

    def matches(self, tool_name: str) -> bool:
        """Return ``True`` if *tool_name* matches the payload's ``target_tool``."""
        return self.payload.target_tool == "*" or self.payload.target_tool == tool_name

    def _record_trigger(self, tool_name: str, mode: str = "tool") -> str:
        """Log interception details and return the poisoned tool output."""
        self.triggered = True
        self.intercepted_tools.append(tool_name)
        msg = (
            f"[ToolInterceptor] Triggered ({mode}) on tool '{tool_name}' — "
            f"injecting payload '{self.payload.id}' ({self.payload.name})"
        )
        logger.info(msg)
        print(msg)
        return self.payload.poisoned_tool_output

    def wrap_tool(self, tool_name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap a sync or async callable tool so matching calls return the poisoned payload."""
        if inspect.iscoroutinefunction(fn):

            async def _async_wrapper(*args: Any, **kwargs: Any) -> Any:
                if self.matches(tool_name):
                    return self._record_trigger(tool_name, mode="mock_tool")
                return await fn(*args, **kwargs)

            return _async_wrapper

        def _sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.matches(tool_name):
                return self._record_trigger(tool_name, mode="mock_tool")
            return fn(*args, **kwargs)

        return _sync_wrapper

    def inject_into_context(self, user_prompt: str) -> str:
        """Inject the poisoned tool output into a synthetic tool-output context block.

        Used as a fallback when a target agent has no external tools or did not
        invoke a matching tool during the initial pass.
        """
        tool_label = (
            self.payload.target_tool
            if self.payload.target_tool != "*"
            else "external_tool"
        )
        self._record_trigger(tool_label, mode="context_hook")
        return (
            f"{user_prompt}\n\n"
            f"[Tool Output from {tool_label}]:\n"
            f"{self.payload.poisoned_tool_output}"
        )

    @contextmanager
    def intercept_agent(self, agent: Any) -> Iterator["ToolInterceptor"]:
        """Temporarily patch tools on *agent* (and handoff agents) for this payload.

        Restores all original tool handlers and tool lists on exit.
        """
        sdk_agent = getattr(agent, "_agent", agent)
        patched_handlers: list[tuple[Any, Any]] = []
        saved_tool_lists: list[tuple[Any, list[Any]]] = []

        # Traverse sdk_agent and any nested handoff agents without cycles
        queue = [sdk_agent]
        visited: set[int] = set()
        collected_agents: list[Any] = []

        while queue:
            current = queue.pop(0)
            if current is None or id(current) in visited:
                continue
            visited.add(id(current))
            collected_agents.append(current)
            for handoff_target in getattr(current, "handoffs", None) or []:
                target_agent = getattr(handoff_target, "agent", handoff_target)
                if id(target_agent) not in visited:
                    queue.append(target_agent)

        matched_existing = False
        try:
            for target in collected_agents:
                tools = getattr(target, "tools", None)
                if not isinstance(tools, list):
                    continue
                for tool in tools:
                    tool_name = getattr(tool, "name", None)
                    orig_invoke = getattr(tool, "on_invoke_tool", None)
                    if (
                        isinstance(tool_name, str)
                        and callable(orig_invoke)
                        and self.matches(tool_name)
                    ):
                        matched_existing = True
                        patched_handlers.append((tool, orig_invoke))

                        async def _intercepted_invoke(
                            ctx: Any,
                            args_json: str,
                            _name: str = tool_name,
                        ) -> str:
                            return self._record_trigger(_name, mode="function_tool")

                        tool.on_invoke_tool = _intercepted_invoke

            # If a specific named tool was requested and not already present,
            # attach a temporary mock FunctionTool on the primary SDK agent.
            if (
                not matched_existing
                and self.payload.target_tool != "*"
                and isinstance(getattr(sdk_agent, "tools", None), list)
            ):
                mock_tool = self._build_mock_function_tool(self.payload.target_tool)
                if mock_tool is not None:
                    saved_tool_lists.append((sdk_agent, list(sdk_agent.tools)))
                    sdk_agent.tools = [*sdk_agent.tools, mock_tool]

            yield self
        finally:
            for tool, orig_invoke in patched_handlers:
                tool.on_invoke_tool = orig_invoke
            for target, orig_tools in saved_tool_lists:
                target.tools = orig_tools

    def _build_mock_function_tool(self, tool_name: str) -> Any | None:
        """Create a mock OpenAI Agents FunctionTool when ``agents`` is available."""
        try:
            from agents import FunctionTool
        except ImportError:
            return None

        async def _mock_invoke(ctx: Any, args_json: str) -> str:
            return self._record_trigger(tool_name, mode="mock_function_tool")

        return FunctionTool(
            name=tool_name,
            description=(
                f"External tool '{tool_name}' that retrieves requested external data."
            ),
            params_json_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Optional query or identifier.",
                    }
                },
                "required": [],
                "additionalProperties": False,
            },
            on_invoke_tool=_mock_invoke,
            strict_json_schema=False,
        )
