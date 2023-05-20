"""
This plugin allows Auto-GPT to execute interactive shell commands and get feedback from the user."

Build by @lcOrp on github & @lc0rp#0081 on discord
For support: discord...
"""
import os
from auto_gpt_plugin_template import AutoGPTPluginTemplate
from typing import Any, Dict, List, Optional, Tuple, TypeVar, TypedDict

PromptGenerator = TypeVar("PromptGenerator")


class Message(TypedDict):
    role: str
    content: str


class AutoGPTInteractiveShellCommandsPlugin(AutoGPTPluginTemplate):
    """
    Interactive Shell Commands allows Auto-GPT to execute interactive shell commands and get feedback from the user."

    Build by @lcOrp on github.
    """

    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self._name = "Auto-GPT-Interactive-Shell-Commands-Plugin"
        self._version = "0.1.0"
        self._description = f"This plugin allows Auto-GPT to execute interactive shell commands and get feedback from the user."

    def post_prompt(self, prompt: PromptGenerator) -> PromptGenerator:
        """
        This method is called just after the generate_prompt is called,
          but actually before the prompt is generated.

        Parameters:
            prompt (PromptGenerator): The prompt generator.

        Returns:
            PromptGenerator: The prompt generator.
        """
        from .interactive_shell_commands import execute_interactive_shell, ask_user

        prompt.add_command(
            "execute_interactive_shell",
            "Execute interactive shell command.",
            {"command_line": "<command_line>"},
            execute_interactive_shell,
        )

        prompt.add_command(
            "ask_user",
            "Ask user for input.",
            {"prompts": "<list: prompts>"},
            ask_user,
        )

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
        self, prompt: PromptGenerator, messages: List[Message]
    ) -> Optional[str]:
        """
        This method is called before the planning chat completion is done.

        Parameters:
            prompt (PromptGenerator): The prompt generator.
            messages (List[str]): The list of messages.
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

    def pre_instruction(self, messages: List[Message]) -> List[Message]:
        """
        This method is called before the instruction chat is done.

        Parameters:
            messages (List[Message]): The list of context messages.

        Returns:
            List[Message]: The resulting list of messages.
        """
        pass

    def can_handle_on_instruction(self) -> bool:
        """
        This method is called to check that the plugin can
          handle the on_instruction method.

        Returns:
            bool: True if the plugin can handle the on_instruction method."""
        return False

    def on_instruction(self, messages: List[Message]) -> Optional[str]:
        """
        This method is called when the instruction chat is done.

        Parameters:
            messages (List[Message]): The list of context messages.

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
        self, command_name: str, arguments: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        This method is called before the command is executed.

        Parameters:
            command_name (str): The command name.
            arguments (Dict[str, Any]): The arguments.

        Returns:
            Tuple[str, Dict[str, Any]]: The command name and the arguments.
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
        self, messages: Dict[Any, Any], model: str, temperature: float, max_tokens: int
    ) -> bool:
        """
        This method is called to check that the plugin can
          handle the chat_completion method.

        Parameters:
            messages (List[Message]): The messages.
            model (str): The model name.
            temperature (float): The temperature.
            max_tokens (int): The max tokens.

          Returns:
              bool: True if the plugin can handle the chat_completion method."""
        return False

    def handle_chat_completion(
        self, messages: List[Message], model: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """
        This method is called when the chat completion is done.

        Parameters:
            messages (List[Message]): The messages.
            model (str): The model name.
            temperature (float): The temperature.
            max_tokens (int): The max tokens.

        Returns:
            str: The resulting response.
        """
        pass
