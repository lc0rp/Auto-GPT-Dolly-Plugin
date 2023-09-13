"""
Dolly is a powerful plugin package designed to extend the capabilities of Auto-GPT by enabling 
it to generate expert agents by starting new Auto-GPT processes, aka cloning itself. 

These agents possess the same knowledge and access to the same suite of tools as Auto-GPT and can perform
tasks in parallel to enable faster, collaborative generation of results. These expert agents can also 
interpret and execute the same commands as Auto-GPT, ensuring consistency and ease of use.

In the future, Auto-GPT shall introduce native multi-agent support within its core. However, until
that goal is achieved, Dolly provides a solution for introducing multi-agent functionality without 
requiring alterations to the AutoGPT core structure.

Build by @lcOrp on github.
For help and discussion: https://discord.com/channels/1092243196446249134/1099609931562369024
"""
import os
from typing import Any, Dict, List, Optional, Tuple, TypedDict, TypeVar

from auto_gpt_plugin_template import AutoGPTPluginTemplate

PromptGenerator = TypeVar("PromptGenerator")


class Message(TypedDict):
    """Message type."""

    role: str
    content: str


LEGACY_CLONE_COMMAND = "clone_autogpt"
# Picked by GPT-4 because it's more descriptive.
CLONE_COMMAND = "deploy_autogpt_expert"
COMMANDS = [
    LEGACY_CLONE_COMMAND,
    CLONE_COMMAND,
    "call_dolly",
    "dolly",
    "call_agent",
    "start_agent",
]


class AutoGPTDollyPlugin(AutoGPTPluginTemplate):
    """
    Dolly is a powerful plugin package designed to extend the capabilities of Auto-GPT by enabling
    it to generate expert agents by starting new Auto-GPT processes, aka cloning itself.

    These agents possess the same knowledge and access to the same suite of tools as Auto-GPT and can perform
    tasks in parallel to enable faster, collaborative generation of results. These expert agents can also
    interpret and execute the same commands as Auto-GPT, ensuring consistency and ease of use.

    In the future, Auto-GPT shall introduce native multi-agent support within its core. However, until
    that goal is achieved, Dolly provides a solution for introducing multi-agent functionality without
    requiring alterations to the AutoGPT core structure.
    """

    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self._name = "Auto-GPT-Dolly-Plugin"
        self._version = "0.3.1"
        self._command = os.getenv("DOLLY_COMMAND", CLONE_COMMAND)
        self._description = f"This plugin adds a '{self._command}' command that lets Auto-GPT build expert agents. For help and discussion: https://discord.com/channels/1092243196446249134/1099609931562369024"

        # Enable debug mode (--debug)
        self.debug = os.getenv("DOLLY_DEBUG", "False") == "True"

        # Limit the number of clones
        self.max_num = int(os.getenv("DOLLY_MAX_NUM", "5"))

        # Enable continuous mode (--continuous) & set continuous limit
        self.continuous_mode = os.getenv("DOLLY_CONTINUOUS_MODE", "True") == "True"
        self.continuous_limit = int(os.getenv("DOLLY_CONTINUOUS_LIMIT", "5"))

        # Separate memory.
        # This gets passed as an environment variable to the model,
        # overriding what's in the .env file.
        # See each memory backend for more details.
        self.separate_memory_index = (
            os.getenv("DOLLY_SEPARATE_MEMORY_INDEX", "False") == "True"
        )

        # Separate settings (--ai-settings)
        # If this is true, the ai_settings_template.yaml file will be used to generate
        # a new ai_settings.yaml file for each clone.
        self.separate_settings = os.getenv("DOLLY_SEPARATE_SETTINGS", "False") == "True"
        self.settings_template = os.getenv(
            "DOLLY_SETTINGS_TEMPLATE", "ai_settings_template.yaml"
        )

        # Separate instructions
        # This is specific to the wonda prompt method that keeps ai_settings.yaml static between runs
        # And instead uses a separate instructions.txt file for instructions.
        # See: https://github.com/samuelbutler/wonda for details.
        # If this is enabled, an instructions file will be generated with the goals for each clone.
        # The main ai_settings.yaml file must instruct AutoGPT to read and follow instructions
        # in the "instrucitons.txt" file.
        self.separate_instructions = (
            os.getenv("DOLLY_SEPARATE_INSTRUCTIONS", "False") == "True"
        )

        env_var_list = os.getenv("DOLLY_ENV_VARS_LIST", "").split(",")
        self.env_vars = {}
        for key in env_var_list:
            env_var = f"DOLLY_{key.upper()}_LIST"
            self.env_vars[key.upper()] = os.getenv(env_var, "").split(",")

        self.enable_new_terminal_experiment = (
            os.getenv("DOLLY_ENABLE_NEW_TERMINAL_EXPERIMENT", "False") == "True"
        )

        # Print out a summary of the settings
        print(f"Auto-GPT Dolly Plugin Settings (v {self._version}):")
        print("==============================================")
        print(f"  - Command: {self._command}")
        print(f"  - Agents in Debug Mode: {self.debug}")
        print(f"  - Max Agents Num: {self.max_num}")
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
        from .dolly_manager import DollyManager

        description = f"instruct(Start AutoGPT Agent for complex tasks. Alias:{LEGACY_CLONE_COMMAND},Replicate,CreateReplica)"

        prompt.add_command(
            self._command,
            description,
            {
                "name": "<name>",
                "role": "<role>",
                "goals": "<goals_str_csv>",
                "ffm_ocean_traits": "<ffm_ocean_traits_csv_or_0,0,0,0,0>",
                "character_attributes": "<character_attributes_str_csv_optional>",
            },
            DollyManager.deploy_autogpt_expert,
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
