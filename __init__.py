"""
Dolly brings multi-agent support to Auto-GPT.

1. Cloning itself
This plugin enables an Auto-GPT agent to "clone itself", by deploying other Auto-GPT 
agents, just like itself clone itself. 

These agents have access to the same suite of tools as the main Auto-GPT and can perform
tasks in parallel to enable faster, collaborative generation of results. 

2. Agent personas
When used in conjunction with Auto-GPT-Turbo, agents can be created with different personas, 
which give the agent different goals, personalities, and traits.

3. Agent teams and management
The plugin also enables the creation and management of agent teams (flocks)

4. Composition of agents via config files
The plugin also enables composition of agents via config files, which allows setting up of teams 
or individual agents with different goals, personalities, and traits

In the future, Auto-GPT shall introduce native multi-agent support within its core. However, until
that goal is achieved, Dolly provides a solution for introducing multi-agent functionality without 
requiring alterations to the AutoGPT core structure.

Build by @lcOrp on github.
For help and discussion: https://discord.com/channels/1092243196446249134/1099609931562369024
"""
import inspect
from typing import Any, Optional, TypedDict, TypeVar

from auto_gpt_plugin_template import AutoGPTPluginTemplate

PromptGenerator = TypeVar("PromptGenerator")


class Message(TypedDict):
    """Message type."""

    role: str
    content: str


COMMANDS = {
    "clone_agent": {
        "description": "Deploy a copy of the current agent to perform tasks in parallel.",
        "aliases": ["clone", "replicate", "create_replica"],
    },
    "create_agent": {
        "description": "Deploy a new, specialized agent to perform tasks in parallel.",
        "aliases": ["create_agent", "create_agent", "call_agent", "spawn"],
    },
}


class AutoGPTDollyPlugin(AutoGPTPluginTemplate):
    def __init__(self):
        super().__init__()
        self.name = "Auto-GPT Dolly Plugin"
        self.version = "0.4.0"
        self.description = "Dolly brings multi-agent support to Auto-GPT."
        self.author = "lcOrp"

        # Plugin settings
        self.debug = False
        self.max_agents = 5
        self.continuous_mode = False
        self.continuous_limit = 5
        self.separate_memory_index = False
        self.separate_settings = False
        self.separate_instructions = False

        # Print out a summary of the settings
        print(f"\n\nAuto-GPT Dolly Plugin Settings (v {self._version}):")
        print("==============================================")
        print(f"  - Commands: {', '.join(COMMANDS.keys())}")
        print(f"  - Agents in Debug Mode: {self.debug}")
        print(f"  - Max Agents Num: {self.max_agents}")
        print(f"  - Agents in Continuous Mode: {self.continuous_mode}")
        print(f"  - Agents Continuous Mode Max Cycles: {self.continuous_limit}")
        print(f"  - Separate Memory Per Agent: {self.separate_memory_index}")
        print(
            f"  - Separate Settings Per Agent: {'Configured (See .env)' if self.separate_settings else 'None'}"
        )
        print(
            f"  - Separate Instructions Per Agent: {'Configured (See .env)' if self.separate_instructions else 'None'}"
        )

    def post_prompt(self, prompt: PromptGenerator) -> PromptGenerator:
        """
        This method is called just after the generate_prompt is called,
          but actually before the prompt is generated.

        Parameters:
            prompt (PromptGenerator): The prompt generator.

        Returns:
            PromptGenerator: The prompt generator.
        """
        from .shepherd import Shepherd

        for command, attrs in COMMANDS.items():
            try:
                target = getattr(Shepherd, command)
                aliases = attrs["aliases"]
                # Use the shortest alias as the command label to save tokens
                command_label = (
                    min(aliases + [command], key=len) if aliases else command
                )

                argspec = inspect.getfullargspec(target)
                arg_names = argspec.args
                arg_annotations = argspec.annotations
                params = {}
                for arg_name, arg_annotation in zip(
                    arg_names, arg_annotations.values()
                ):
                    if arg_name in ["cls", "self", "agent"]:
                        continue

                    params[arg_name] = (
                        str(arg_annotation)
                        if "class" not in str(arg_annotation)
                        else arg_annotation.__name__
                    )

                prompt.add_command(
                    command_label=command_label,
                    command_name=attrs["description"],
                    params=params,
                    function=target,
                )
            except AttributeError:
                # TODO: Log error
                pass

        return prompt

    def can_handle_post_prompt(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the post_prompt method.

        Returns:
            bool: True if the plugin can handle the post_prompt method."""
        return True

    def can_handle_on_response(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the on_response method.

        Returns:
            bool: True if the plugin can handle the on_response method."""
        return False

    def on_response(self, response: str, *args, **kwargs) -> Optional[str]:
        """This method is called when a response is received from the model."""
        pass

    def can_handle_on_planning(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the on_planning method.

        Returns:
            bool: True if the plugin can handle the on_planning method."""
        return False

    def on_planning(
        self, prompt: PromptGenerator, messages: list[Message]
    ) -> Optional[str]:
        """
        This method is called before the planning chat completion is done.

        Parameters:
            prompt (PromptGenerator): The prompt generator.
            messages (list[str]): The list of messages.
        """
        pass

    def can_handle_post_planning(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the post_planning method.

        Returns:
            bool: True if the plugin can handle the post_planning method."""
        return False

    def post_planning(self, response: str) -> Optional[str]:
        """
        This method is called after the planning chat completion is done.

        Parameters:
            response (str): The response.

        Returns:
            str: The resulting response.
        """
        pass

    def can_handle_pre_instruction(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the pre_instruction method.

        Returns:
            bool: True if the plugin can handle the pre_instruction method."""
        return False

    def pre_instruction(self, messages: list[Message]) -> list[Message]:
        """
        This method is called before the instruction chat is done.

        Parameters:
            messages (list[Message]): The list of context messages.

        Returns:
            list[Message]: The resulting list of messages.
        """
        pass

    def can_handle_on_instruction(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the on_instruction method.

        Returns:
            bool: True if the plugin can handle the on_instruction method."""
        return False

    def on_instruction(self, messages: list[Message]) -> Optional[str]:
        """
        This method is called when the instruction chat is done.

        Parameters:
            messages (list[Message]): The list of context messages.

        Returns:
            Optional[str]: The resulting message.
        """
        pass

    def can_handle_post_instruction(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the post_instruction method.

        Returns:
            bool: True if the plugin can handle the post_instruction method."""
        return False

    def post_instruction(self, response: str) -> str:
        """
        This method is called after the instruction chat is done.

        Parameters:
            response (str): The response.

        Returns:
            str: The resulting response.
        """
        pass

    def can_handle_pre_command(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the pre_command method.

        Returns:
            bool: True if the plugin can handle the pre_command method."""
        return False

    def pre_command(
        self, command_name: str, arguments: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """
        This method is called before the command is executed.

        Parameters:
            command_name (str): The command name.
            arguments (dict[str, Any]): The arguments.

        Returns:
            tuple[str, dict[str, Any]]: The command name and the arguments.
        """
        # Return "write_to_file" => settings file
        pass

    def can_handle_post_command(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the post_command method.

        Returns:
            bool: True if the plugin can handle the post_command method."""
        return False

    def post_command(self, command_name: str, response: str) -> str:
        """
        This method is called after the command is executed.

        Parameters:
            command_name (str): The command name.
            response (str): The response.

        Returns:
            str: The resulting response.
        """
        pass

    def can_handle_chat_completion(
        self, messages: dict[Any, Any], model: str, temperature: float, max_tokens: int
    ) -> bool:
        """
        This method is called to check that the plugin can
          handle the chat_completion method.

        Parameters:
            messages (list[Message]): The messages.
            model (str): The model name.
            temperature (float): The temperature.
            max_tokens (int): The max tokens.

          Returns:
              bool: True if the plugin can handle the chat_completion method."""
        return False

    def handle_chat_completion(
        self, messages: list[Message], model: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """
        This method is called when the chat completion is done.

        Parameters:
            messages (list[Message]): The messages.
            model (str): The model name.
            temperature (float): The temperature.
            max_tokens (int): The max tokens.

        Returns:
            str: The resulting response.
        """

    def can_handle_text_embedding(self, text: str) -> bool:
        """This method is called to check that the plugin can
          handle the text_embedding method.
        Args:
            text (str): The text to be convert to embedding.
          Returns:
              bool: True if the plugin can handle the text_embedding method."""
        return False

    def handle_text_embedding(self, text: str) -> list:
        """This method is called when the chat completion is done.
        Args:
            text (str): The text to be convert to embedding.
        Returns:
            list: The text embedding.
        """
        pass

    def can_handle_user_input(self, user_input: str) -> bool:
        """This method is called to check that the plugin can
        handle the user_input method.

        Args:
            user_input (str): The user input.

        Returns:
            bool: True if the plugin can handle the user_input method."""
        return False

    def user_input(self, user_input: str) -> str:
        """This method is called to request user input to the user.

        Args:
            user_input (str): The question or prompt to ask the user.

        Returns:
            str: The user input.
        """
        return user_input

    def can_handle_report(self) -> bool:
        """This method is called to check that the plugin can
        handle the report method.

        Returns:
            bool: True if the plugin can handle the report method."""
        return False

    def report(self, message: str) -> None:
        """This method is called to report a message to the user.

        Args:
            message (str): The message to report.
        """
