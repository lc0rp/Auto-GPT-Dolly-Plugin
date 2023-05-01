import json
import os
from pathlib import Path
import platform
import subprocess
from typing import Optional

try:
    from autogpt.config.config import Config
except ImportError:
    from unittest.mock import MagicMock

    Config = MagicMock


from . import AutoGPTDollyPlugin

plugin = AutoGPTDollyPlugin()
cfg = Config()


class Dolly:
    def __init__(self):
        pass

    @staticmethod
    def format_goals_str(goals: str):
        """
        This function formats the input goals string from JSON or a comma-separated format
        into a Markdown list string.

        Parameters:
            goals (str): The input goals string, either in JSON format or as a
            comma-separated list.

        Returns:
            str: A formatted Markdown string with goals listed as bullet points.
        """
        try:
            goals = json.loads(goals)
        except json.decoder.JSONDecodeError:
            goals = (
                goals.replace("[", "")
                .replace("]", "")
                .replace('"', "")
                .replace("'", "")
            )
            goals = goals.split(",")

        if isinstance(goals, str):
            goals = [goals]

        goals = [goal.replace("-", "").strip() for goal in goals]
        goals = [f"- {goal}" for goal in goals]
        goals = "\n".join(goals)
        return goals

    @staticmethod
    def clone_autogpt(
        name: str,
        role: str,
        goals: str,
        big5_personality: Optional[str] = "5,5,3,5,1",
        attributes: Optional[list[str]] = "helpful,encouraging,accurate",
    ):
        """
        Creates a new AutoGPT expert.

        Parameters:
            name (str): The name of the new autogpt instance.
            role (str): The "Act As" role of the new expert (e.g. "A hungry AI")
            goals (str): A comma separated list of goals for the new expert.
            big5_personality (str): A comma separated list of Big 5 scores on a scale of 1-5,
            e.g. "1,2,3,4,5"
            attribues (list(str)): A comma separated list of free form attributes for the
            new expert. e.g. "hungry,smart,funny, like einstein"
        """
        goals = Dolly.format_goals_str(goals)

        workspace_path = Path(cfg.workspace_path)
        if plugin.separate_instructions:
            instructions_file = workspace_path / f"instructions_{name}.txt"
            instructions = f'You\'re an Autonomous AI, NAME={name}, ACT AS ROLE={role}\nWith BIG5_PERSONALITY="{big5_personality}" and ATTRIBUTES="{attributes}".\nGOALS:\n{goals}'
            results = Dolly.write_to_file(instructions_file, instructions)
            assert results.exists()

        if plugin.separate_settings:
            new_settings_file = Dolly.create_settings_file(
                name, role, goals, big5_personality, attributes, workspace_path
            )

        else:
            new_settings_file = Path(cfg.ai_settings_file)

        memory_index = os.getenv("MEMORY_INDEX", "auto-gpt")
        if plugin.separate_memory_index:
            memory_index = f"{memory_index}-{name}"

        debug = "--debug" if plugin.debug else ""

        cmd = f"MEMORY_INDEX={memory_index} python -m autogpt -C {new_settings_file} {debug}"

        if not plugin.enable_interactivity:
            cmd += f" -c -l {plugin.continuous_limit}"

        stdout_file = workspace_path / f"output-{name}.txt"
        stderr_file = workspace_path / f"error-{name}.txt"

        return Dolly.execute_shell_command(
            cmd, stdout_file=str(stdout_file), stderr_file=str(stderr_file)
        )

    @staticmethod
    def execute_shell_command(
        cmd, stdout_file="output.txt", stderr_file="error.txt"
    ) -> str:
        """
        Attempts to open a new terminal window, execute a shell command with Popen and return an english description
          of the event and the process id. It falls back to the same terminal if it can't open a new one.

        Args:
            cmd (str): The cmd to run in the new terminal

        Returns:
            str: Success message and ID of the new process
        """
        with open(stdout_file, "w") as fout, open(stderr_file, "w") as ferr:
            result = subprocess.Popen(cmd, stdout=fout, stderr=ferr, shell=True)

        return f"Subprocess started with PID: {result.pid}"

    @staticmethod
    def execute_shell_command_old(
        cmd, stdout_file="output.txt", stderr_file="error.txt"
    ) -> str:
        """
        Attempts to open a new terminal window, execute a shell command with Popen and return an english description
          of the event and the process id. It falls back to the same terminal if it can't open a new one.

        Args:
            cmd (str): The cmd to run in the new terminal

        Returns:
            str: Success message and ID of the new process
        """
        current_dir = os.getcwd()

        # Change dir into workspace if necessary
        if cfg.workspace_path not in current_dir:
            os.chdir(cfg.workspace_path)

        result = False
        new_terminal_cmd = ""
        creationflags = 0

        if plugin.enable_new_terminal_experiment:
            system = platform.system()
            # Mac terminal
            if system == "Darwin":
                new_terminal_cmd = [
                    "open",
                    "-a",
                    "Terminal",
                    "-n",
                    "--args",
                    "bash",
                    "-c",
                    cmd,
                ]

            # Windows cmd
            elif system == "Windows":
                new_terminal_cmd = ["start", "cmd.exe", "/k", cmd]
                creationflags = subprocess.CREATE_NEW_CONSOLE

            # Linux terminal
            else:
                new_terminal_cmd = ["gnome-terminal", "--", "bash", "-c", cmd]

        with open(stdout_file, "w") as fout, open(stderr_file, "w") as ferr:
            try:
                result = subprocess.Popen(
                    new_terminal_cmd,
                    stdout=fout,
                    stderr=ferr,
                    creationflags=creationflags,
                    shell=True,
                )
            except FileNotFoundError:
                print("Error: Could not launch a new terminal.")

            if not result:
                result = subprocess.Popen(cmd, stdout=fout, stderr=ferr, shell=True)

        os.chdir(current_dir)

        return f"Subprocess started with PID: {result.pid}"

    @staticmethod
    def create_settings_file(
        name, role, goals, big5_personality, attributes, workspace_path
    ):
        """
        Creates a new settings file for an AutoGPT clone.

        Parameters:
            name (str): The name of the new clone.
            role (str): The "Act As" role of the new clone (e.g. "A hungry AI")
            goals (str): A bulleted list of goals for the new clone.
            big5_personality (str): A comma separated list of Big 5 scores on a scale of 1-5,
            e.g. "1,2,3,4,5"
            attribues (list(str)): A comma separated list of free form attributes for the
            new clone. e.g. "hungry,smart,funny, like einstein"

        Returns:
            str: The name of the new settings file.
        """
        if plugin.settings_template:
            settings_file = plugin.settings_template
        else:
            settings_file = cfg.ai_settings_file

        settings_filepath = workspace_path / settings_file

        new_settings_file = f"ai_settings_{name}.yaml"
        new_settings_filepath = workspace_path / new_settings_file
        with open(settings_filepath, "r") as f:
            settings = f.read()

            replace_map = {
                "<CLONE_NAME>": name,
                "<REPLICA_NAME>": name,
                "<EXPERT_NAME>": name,
                "<NAME>": name,
                "{ai_name}": name,
            }

            # If personality placeholders are not in the settings file, add them to the role
            if (
                big5_personality
                and big5_personality.lower() != "none"
                and big5_personality.strip() != ""
            ):
                if "<BIG5_PERSONALITY>" in settings:
                    replace_map["<BIG5_PERSONALITY>"] = big5_personality.strip()
                else:
                    role += f' with BIG5_PERSONALITY="{big5_personality.strip()}"'

            # If attribute placeholders are not in the settings file, add them to the role
            if attributes and attributes.lower() != "none" and attributes.strip() != "":
                if "<ATTRIBUTES>" in settings:
                    replace_map["<ATTRIBUTES>"] = attributes
                else:
                    role += f' with ATTRIBUTES="{attributes}"'

            # If role placeholders are not in the settings file, prepend the role to the goals
            role_replacements = {
                "<CLONE_ROLE>": role,
                "<REPLICA_ROLE>": role,
                "<EXPERT_ROLE>": role,
                "<ROLE>": role,
            }

            if any(
                [placeholder in settings for placeholder in role_replacements.keys()]
            ):
                replace_map.update(role_replacements)
            else:
                goals = f"- ACT AS ROLE={role}\n{goals}"

            replace_map.update(
                {
                    "<CLONE_GOALS>": goals,
                    "<REPLICA_GOALS>": goals,
                    "<EXPERT_GOALS>": goals,
                    "<GOALS>": goals,
                }
            )
        for old, new in replace_map.items():
            settings = settings.replace(old, new)

        result = Dolly.write_to_file(new_settings_filepath, settings)
        assert result.exists()
        return new_settings_filepath

    @staticmethod
    def write_to_file(filepath: Path, text: str):
        """
        Writes text to a file. (Stub for testing)

        Parameters:
            filepath (str): The path to the file to write to.
            text (str): The text to write to the file.
        """
        filepath.write_text(text)
        return filepath
