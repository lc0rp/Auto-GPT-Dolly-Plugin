from copy import deepcopy
from datetime import datetime

from autogpt.agents import Agent
from autogpt.app.configurator import create_config
from autogpt.app.main import construct_main_ai_config, run_interaction_loop
from autogpt.config.config import GPT_3_MODEL, GPT_4_MODEL
from autogpt.config.prompt_config import PromptConfig
from autogpt.memory.vector import get_memory
from turbo.personas.manager import PersonaManager


class Shepherd:
    @classmethod
    def clone_agent(cls, goals: list[str], agent: Agent) -> str:
        new_name = f"{agent.ai_config.ai_name}-c[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
        return cls.create_agent(
            name=new_name,
            role=agent.ai_config.ai_role,
            goals=goals,
            backstory="",
            persona="",
            personality="",
            agent=agent,
        )

    @classmethod
    def create_agent(
        cls,
        name: str,
        role: str,
        goals: list[str],
        backstory: str,
        persona: str,
        personality: str,
        agent: Agent,
    ) -> str:
        if persona:
            ai_settings_file, prompt_settings_file = PersonaManager.load(persona)
        else:
            ai_settings_file = agent.config.ai_settings_file
            prompt_settings_file = agent.config.prompt_settings_file

        config = deepcopy(agent.config)
        create_config(
            config=config,
            continuous=config.continuous_mode,
            continuous_limit=config.continuous_limit,
            ai_settings_file=ai_settings_file,
            prompt_settings_file=prompt_settings_file,
            skip_reprompt=config.skip_reprompt,
            speak=config.speak_mode,
            debug=config.debug_mode,
            gpt3only=(
                config.fast_llm == config.smart_llm and config.fast_llm == GPT_3_MODEL
            ),
            gpt4only=(
                config.fast_llm == config.smart_llm and config.fast_llm == GPT_4_MODEL
            ),
            memory_type=config.memory_backend,
            browser_name=config.selenium_web_browser or None,
            allow_downloads=config.allow_downloads,
            skip_news=config.skip_news,
        )

        # only combine role, backstory and personality if they are not empty
        if backstory:
            role = ", ".join([role, backstory])
        if personality:
            role = ", ".join([role, personality])

        ai_config = construct_main_ai_config(
            config,
            name=name,
            role=role,
            goals=goals,
        )

        ai_config.command_registry = agent.command_registry
        new_agent = Agent(
            memory=get_memory(config),
            command_registry=ai_config.command_registry,
            ai_config=ai_config,
            config=config,
            triggering_prompt=PromptConfig(
                config.prompt_settings_file
            ).triggering_prompt,
        )

        # TODO: Make run_interactive_loop async
        try:
            run_interaction_loop(new_agent)
        except SystemExit:
            return f"Agent '{name}' run and exited successfully."
        return None
