from agentic_radar.graph import Agent

from .pipeline import PromptEnhancingPipeline


def enhance_agent_prompts(
    agents: list[Agent], pipeline: PromptEnhancingPipeline
) -> dict[str, str]:
    """Enhance the system prompts of the agents.

    Args:
        agents (list[Agent]): List of agents with system prompts to enhance.
        pipeline (PromptEnhancingPipeline): The pipeline to use for enhancing prompts.

    Returns:
        dict[str, str]: Dictionary mapping agent names to their enhanced system prompts.
    """

    enhanced_prompts = {}
    for agent in agents:
        try:
            enhanced_prompt = pipeline.run(agent.system_prompt)
            enhanced_prompts[agent.name] = enhanced_prompt
        except Exception as e:
            print(f"Error enhancing prompt for agent {agent.name}: {e}")
            enhanced_prompts[agent.name] = agent.system_prompt

    return enhanced_prompts
