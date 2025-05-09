from agentic_radar.graph import Agent

from .pipeline import PromptHardeningPipeline


def harden_agent_prompts(
    agents: list[Agent], pipeline: PromptHardeningPipeline
) -> dict[str, str]:
    """Harden the system prompts of the agents.

    Args:
        agents (list[Agent]): List of agents with system prompts to harden.
        pipeline (PromptHardeningPipeline): The pipeline to use for hardening prompts.

    Returns:
        dict[str, str]: Dictionary mapping agent names to their hardened system prompts.
    """

    hardened_prompts = {}
    for agent in agents:
        try:
            hardened_prompt = pipeline.run(agent.system_prompt)
            hardened_prompts[agent.name] = hardened_prompt
        except Exception as e:
            print(f"Error hardening prompt for agent {agent.name}: {e}")
            hardened_prompts[agent.name] = agent.system_prompt

    return hardened_prompts
