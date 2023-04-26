import os

from autogpt.config.config import Config

from . import AutoGPTDollyPlugin
from autogpt.commands.execute_code import execute_shell_popen
from autogpt.commands.file_operations import write_to_file

plugin = AutoGPTDollyPlugin()
cfg = Config()


def create_clone(name: str, goals: str):
    if plugin.separate_instructions:
        # Create instructions
        instructions_file = cfg.workspace_path + f"/instructions_{name}.txt"
        write_to_file(instructions_file, goals)
    
    if plugin.separate_settings:
        if plugin.settings_template:
            settings_file = plugin.settings_template
        else:
            settings_file = cfg.ai_settings_file
            
        settings_filepath =  cfg.workspace_path + "/" + settings_file

        new_settings_file = f"ai_settings_{name}.yaml"
        new_settings_filepath = cfg.workspace_path + "/" + new_settings_file
        # Create settings file
        # Replace <CLONE_NAME> with the clone name
        # Replace <CLONE_GOALS> with the clone goals
        with open(settings_filepath, "r") as f:
            settings = f.read()
            settings = settings.replace("<CLONE_NAME>", name)
            settings = settings.replace("<REPLICA_NAME>", name)
            settings = settings.replace("{ai_name}", name)
            settings = settings.replace("<CLONE_GOALS>", goals)
            settings = settings.replace("<REPLICA_GOALS>", goals)
            write_to_file(new_settings_filepath, settings)
            
    else:
        new_settings_file = cfg.ai_settings_file

    # Update memory variable
    memory_index = os.getenv("MEMORY_INDEX", "auto-gpt")
    if plugin.separate_memory_index:
        memory_index = f"{memory_index}-{name}"
        
    debug = "--debug" if plugin.debug else ""
    execute_shell_popen(f"cd {cfg.workspace_path} && MEMORY_INDEX={memory_index} python -m autogpt -c -l {plugin.continuous_limit} -C {new_settings_file} {debug}")
    
def replicate(name: str, goals: str):
    """'Replicate' is less confusing for GPT 3.5
    """
    create_clone(name, goals)