import os
from auto_gpt_plugin_template import AutoGPTPluginTemplate
from typing import Any, Dict, List, Optional, Tuple, TypeVar, TypedDict

PromptGenerator = TypeVar("PromptGenerator")


class Message(TypedDict):
    role: str
    content: str


CLONE_CMD = "clone_autogpt"


class AutoGPTDollyPlugin(AutoGPTPluginTemplate):
    """
    AutoGPTDolly is a cloner plugin for Auto-GTP. This plugin adds the command: clone_autogpt
    """

    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self._name = "Auto-GPT-Dolly-Plugin"
        self._version = "0.3.0"
        self._description = f"This plugin adds a {CLONE_CMD} command that lets Auto-GPT build an army of powerful minions."

        # Enable debug mode (--debug)
        self.debug = os.getenv("DOLLY_DEBUG", "False") == "True"

        # Limit the number of clones
        self.max_num = int(os.getenv("DOLLY_MAX_NUM", 5))

        # Enable continuous mode (--continuous) & set continuous limit
        self.continuous_mode = os.getenv("DOLLY_CONTINUOUS_MODE", "True") == "True"
        self.continuous_limit = int(os.getenv("DOLLY_CONTINUOUS_LIMIT", 5))

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

        prompt.add_command(
            CLONE_CMD,
            "instruct(Clone AutoGPT for complex tasks. Alias:Replicate,CreateReplica)",
            {
                "name": "<name>",
                "role": "<role>",
                "goals": "<goals_str_csv>",
                "ffm_ocean_traits": "<ffm_ocean_traits_csv_or_0,0,0,0,0>",
                "character_attributes": "<character_attributes_str_csv_optional>",
            },
            DollyManager.clone_autogpt,
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