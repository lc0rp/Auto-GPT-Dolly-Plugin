import json
from pathlib import Path
from typing import Optional

from . import AutoGPTDollyPlugin
from .flock import Flock

plugin = AutoGPTDollyPlugin()


class DollyManager:
    @classmethod
    def deploy_autogpt_expert(
        cls,
        name: str,
        role: str,
        goals: str,
        ffm_ocean_traits: Optional[str] = "5,5,3,5,1",
        character_attributes: Optional[list[str]] = "helpful,encouraging,accurate",
    ):
        """
        Creates and deploys new AutoGPT expert agent.
        Parameters:
            name (str): The name of the new autogpt instance.
            role (str): The "Act As" role of the new expert (e.g. "A hungry AI")
            goals (str): A comma separated list of goals for the new expert.
            ffm_ocean_traits (str): A comma separated list of FFM (Big 5, or OCEAN) scores on a scale of 1-5,
            e.g. "1,2,3,4,5"
            character_attributes (list(str)): A comma separated list of free form attributes for the
            new expert. e.g. "hungry,smart,funny, like einstein"
        """
        flock = Flock(max_size=plugin.max_num)

        try:
            goals = json.loads(goals)
        except json.decoder.JSONDecodeError:
            goals = (
                str(goals)
                .replace("[", "")
                .replace("]", "")
                .replace('"', "")
                .replace("'", "")
            )
            goals = goals.split(",")

        from .dolly import Dolly

        new_expert = Dolly(
            name=name,
            role=role,
            goals=goals,
            continuous_mode=plugin.continuous_mode,
            continuous_limit=plugin.continuous_limit,
            ffm_ocean_traits=[int(score) for score in ffm_ocean_traits.split(",")],
            character_attributes=character_attributes.split(","),
        )

        flock.add_member(new_expert)
        pids = flock.disperse()
        if pids:
            return f"Subprocess started with PID: {pids[0]}"

    @staticmethod
    def write_to_file(filepath: Path, text: str):
        """
        Writes text to a file. (Stub for testing)
        Parameters:
            filepath (str): The path to the file to write to.
            text (str): The text to write to the file.
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(text)
        return filepath
