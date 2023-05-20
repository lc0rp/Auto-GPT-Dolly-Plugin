"""Execute interactive shell commands in the workspace"""
import os
import subprocess
from pathlib import Path
import sys

from autogpt.config import Config
from autogpt.logs import logger

CFG = Config()


def execute_interactive_shell(command_line: str) -> str:
    """Execute a shell command that requires interactivity and return the output

    Args:
        command_line (str): The command line to execute

    Returns:
        str: The output of the command
    """
    current_dir = Path.cwd()
    # Change dir into workspace if necessary
    if not current_dir.is_relative_to(CFG.workspace_path):
        os.chdir(CFG.workspace_path)

    logger.info(
        f"Executing command '{command_line}' in working directory '{Path.cwd()}'"
    )

    process = subprocess.Popen(
        command_line,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    def read_output(pipe):
        while True:
            byte_output = pipe.readline()
            if byte_output == b"":
                break
            output = byte_output.decode("utf-8")
            eof_sequence = "\x04"  # Enter this sequence to terminate user input

            sys.stdout.write(output)
            if EOFError(eof_sequence):  # Use EOFError here
                user_input = os.read(sys.stdin.fileno(), 1024)
                process.stdin.write(user_input)
                process.stdin.flush()

    read_output(process.stdout)
    read_output(process.stderr)
    result = process.communicate()

    # Change back to the prior working dir
    os.chdir(current_dir)

    output = f"STDOUT:\n{result[0]}\nSTDERR:\n{result[1]}"
    return output


def ask_user(prompts: list[str]) -> list[str]:
    """
    Ask the user a series of prompts and return the responses

    Args:
        prompts (list[str]): The prompts to ask the user

    Returns:
        list[str]: The responses from the user
    """
    results = []
    for prompt in prompts:
        response = input(prompt)
        results.append(response)
    return results
