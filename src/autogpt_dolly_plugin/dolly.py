import os
from pathlib import Path
import platform
import subprocess

try:
    from autogpt.config.config import Config
except ImportError:
    from unittest.mock import MagicMock

    Config = MagicMock


from . import AutoGPTDollyPlugin

plugin = AutoGPTDollyPlugin()
cfg = Config()


class Dolly:
    def __init__(
        self,
        name: str,
        role: str,
        goals: list[str],
        continuous_mode: bool,
        continuous_limit: int = 5,
        ffm_ocean_traits: list[int] = [5, 5, 3, 5, 1],
        character_attributes: list[str] = ["helpful", "encouraging", "accurate"],
    ):
        # Attributes
        self.name = name
        self.role = role
        self.goals = goals
        self.continuous_mode = continuous_mode
        self.continuous_limit = continuous_limit
        self.ffm_ocean_traits = ffm_ocean_traits
        self.character_attributes = character_attributes
        self.workspace_path = Path(cfg.workspace_path)

        # Flags to track if we've been dispersed yet.
        self._process: subprocess.Popen = None
        self._index: int = None
        self._instructions_dispersed: bool = False
        self._settings_dispersed: bool = False

    @property
    def dispersed(self):
        return self._process is not None

    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, value: subprocess.Popen):
        if self._process is not None:
            raise ValueError("Cannot set process more than once.")
        self._process = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value: int):
        if self.index is not None:
            raise ValueError("Cannot set index more than once.")
        if not isinstance(value, int):
            raise ValueError("Index must be an integer.")
        self._index = value

    @property
    def goals_as_str(self):
        return "- " + ("\n- ".join(self.goals)) if self.goals else ""

    @property
    def ffm_ocean_traits_as_str(self):
        return ",".join(str(score) for score in self.ffm_ocean_traits)

    @property
    def character_attributes_as_str(self):
        return ",".join(self.character_attributes)

    def disperse(self):
        if self.process:
            raise ValueError(
                f"Cannot disperse more than once. Already dispersed with PID={self.process.pid}"
            )

        self._disperse_instructions()
        self._disperse_settings()
        self._disperse_shell_process()
        self.deployed = True

        if self.process:
            return self.process.pid

    def _disperse_instructions(self):
        if self._instructions_dispersed:
            raise ValueError("Instructions already dispersed.")

        if not plugin.separate_instructions:
            self._instructions = None
            self._instructions_dispersed = True
            return

        instructions_file = self.workspace_path / self.name / "instructions.txt"
        self._instructions = (
            f"You're an Autonomous AI, NAME={self.name},"
            f" ACT AS ROLE={self.role}\nWith FFM_OCEAN_TRAITS='{self.ffm_ocean_traits_as_str}'"
            f" and CHARACTER_ATTRIBUTES='{self.character_attributes_as_str}'"
            f" \nGOALS:\n{self.goals_as_str}"
        )
        from .dolly_manager import DollyManager

        results_file = DollyManager.write_to_file(instructions_file, self._instructions)
        self._instructions_dispersed = results_file.exists()

    def _disperse_settings(self):
        if not self._instructions_dispersed:
            raise ValueError("Disperse instructions before settings.")

        if self._settings_dispersed:
            raise ValueError("Settings already dispersed.")

        if not plugin.separate_settings:
            self.settings_filepath = (
                Path(cfg.ai_settings_file)
                if Path(cfg.ai_settings_file).is_absolute()
                else self.workspace_path / cfg.ai_settings_file
            )
            self._settings_dispersed = True
        else:
            if plugin.settings_template:
                template_file = plugin.settings_template
            else:
                template_file = cfg.ai_settings_file

            source_path = (
                Path(template_file)
                if Path(template_file).is_absolute()
                else self.workspace_path / template_file
            )

            self.settings_filepath = (
                self.workspace_path / self.name / "ai_settings.yaml"
            )

            settings = source_path.read_text()

            # Replace name placeholders
            settings = settings.replace("<NAME>", self.name)

            role = self.role
            # If personality placeholders are not in the settings file, add them to the role
            scores_as_str = self.ffm_ocean_traits_as_str
            if "<FFM_OCEAN_TRAITS>" in settings:
                settings = settings.replace("<FFM_OCEAN_TRAITS>", scores_as_str.strip())
            else:
                role += f" with FFM_OCEAN_TRAITS='{scores_as_str.strip()}'"

            # If attribute placeholders are not in the settings file, add them to the role
            attributes_as_str = self.character_attributes_as_str
            if "<CHARACTER_ATTRIBUTES>" in settings:
                settings = settings.replace(
                    "<CHARACTER_ATTRIBUTES>", attributes_as_str.strip()
                )
            else:
                role += f' with ATTRIBUTES="{attributes_as_str.strip()}"'

            # If role placeholders are not in the settings file, prepend the role to the goals
            goals = self.goals_as_str.strip()
            if "<ROLE>" in settings:
                settings = settings.replace("<ROLE>", role)
            else:
                goals = f"- ACT AS ROLE={role}\n{goals}"

            settings = settings.replace("<GOALS>", goals)
            self._settings = settings

            from .dolly_manager import DollyManager

            results_file = DollyManager.write_to_file(self.settings_filepath, settings)
            self._settings_dispersed = results_file.exists()

    def _disperse_shell_process(self):
        if not self._settings_dispersed:
            raise ValueError("Disperse settings before shell process.")

        if self.dispersed:
            raise ValueError("Already dispersed.")

        self.memory_index = os.getenv("MEMORY_INDEX", "auto-gpt")
        if plugin.separate_memory_index:
            self.memory_index = f"{self.memory_index}-{self.name}"

        env_vars = {"MEMORY_INDEX": self.memory_index}
        for key, value in plugin.env_vars.items():
            env_vars[key] = value[self.index]

        cmd = []
        for key, value in env_vars.items():
            cmd += [f"{key}={value}"]

        cmd += [
            f"",
            "python",
            "-m",
            "autogpt",
            "-C",
            self.settings_filepath,
        ]

        if plugin.debug:
            cmd.append("--debug")

        if plugin.continuous_mode:
            cmd += ["-c", "-l", str(plugin.continuous_limit)]

        self._shell_cmd = cmd

        stdout_file = self.workspace_path / self.name / "output.txt"
        stderr_file = self.workspace_path / self.name / "error.yaml"

        with open(stdout_file, "w") as fout, open(stderr_file, "w") as ferr:
            self.process = subprocess.Popen(cmd, stdout=fout, stderr=ferr, shell=True)
