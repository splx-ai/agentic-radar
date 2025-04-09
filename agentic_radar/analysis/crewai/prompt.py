from agentic_radar.analysis.crewai.models import CrewAIAgent


def build_system_prompt(agent: CrewAIAgent) -> str:
    try:
        from crewai.utilities.prompts import I18N, Prompts  # type: ignore
    except ImportError:
        raise ImportError("Please install the crewai package to use this feature.")

    i18n = I18N()
    prompts = Prompts(
        i18n=i18n,
        tools=agent.tools,
        system_template=agent.system_template,
        prompt_template=agent.prompt_template,
        response_template=agent.response_template,
        use_system_prompt=agent.use_system_prompt,
        agent=agent,
    )

    built_prompts = prompts.task_execution()

    return (
        built_prompts["system"]
        if "system" in built_prompts
        else built_prompts["prompt"]
    )
