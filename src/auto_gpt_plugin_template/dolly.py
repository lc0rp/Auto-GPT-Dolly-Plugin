import os

from autogpt.config.config import Config
from autogpt.workspace import path_in_workspace

from . import AutoGPTDollyPlugin
from autogpt.commands.execute_code import execute_shell_popen
from autogpt.commands.file_operations import write_to_file

plugin = AutoGPTDollyPlugin()

def get_settings_filepath():
    settings_file = Config().ai_settings_file
    cwd = os.getcwd()
    return os.path.abspath(os.path.join(cwd, '..', settings_file))

def create_clone(name: str, goals: str):
    if plugin.separate_instructions:
        # Create instructions
        write_to_file(f"instructions_{name}.txt", goals)
    
    if plugin.separate_settings:
        if plugin.settings_template:
            settings_file = plugin.settings_template
            settings_filepath = path_in_workspace(settings_file)
        else:
            settings_filepath = get_settings_filepath()

        new_settings_file = f"ai_settings_clone_{name}.yaml"
        # Create settings file
        # Replace <CLONE_NAME> with the clone name
        # Replace <CLONE_GOALS> with the clone goals
        with open(settings_filepath, "r") as f:
            settings = f.read()
            settings = settings.replace("<CLONE_NAME>", name)
            settings = settings.replace("<REPLICA_NAME>", name)
            settings = settings.replace("<CLONE_GOALS>", goals)
            settings = settings.replace("<REPLICA_GOALS>", goals)
            write_to_file(new_settings_file, settings)
            
        new_settings_filepath = path_in_workspace(new_settings_file)
    else:
        new_settings_filepath = get_settings_filepath()

    # Update memory variable
    memory_index = os.getenv("MEMORY_INDEX", "auto-gpt")
    if plugin.separate_memory_index:
        memory_index = f"{memory_index}-{name}"
        
    debug = "--debug" if plugin.debug else ""
    execute_shell_popen(f"cd .. && MEMORY_INDEX={memory_index} python -m autogpt -c -l {plugin.continuous_limit} -C {new_settings_filepath} {debug}")
    
def replicate(name: str, goals: str):
    """'Replicate' is less confusing for GPT 3.5
    """
    create_clone(name, goals)