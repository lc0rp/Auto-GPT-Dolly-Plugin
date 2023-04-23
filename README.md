# AutoGPTDolly (Beta) - a cloner plugin for Auto-GTP

## Overview

This plugin adds a "create_clone" command that lets Auto-GPT build an army of powerful minions.

AutoGPT can already create AI agents, but sometimes it helps to be able to create additional AutoGTP processes, which can access the tools, plugins and full functionality of AutoGTP.

The "create_clone" command starts a new AutoGPT process, optionally with its own memory, instructions and output files. The processes run in continuous mode for 5 cycles by default. See the Configuration section for how to increase or decrease the number of cycles.

As a bonus, the separate processes run concurrently, which can speed up total execution time for your task.

## Usage

You can tell AutoGPT to clone itself, as part of its tasks:

**Example Goals:**
- Create a clone (choose a name <CLONE_NAME> for it) to search reddit for "topic" and save the results to reddit_results.txt
- Create a second clone (choose a name <CLONE_NAME> for it) to download the latest tweets about "topic" and save the results to twitter_results.txt
- Once the files have been created, compare their contents...

**Limitations:**
- Inter-process communcation is a work in progress. For now, communication is mostly one way, via the instructions or goals that the main process gives to the clones.

## Installation

Download this repository as a .zip file, copy it to ./plugins/, and rename it to Auto-GPT-Dolly-Plugin.zip.

To download it directly from your Auto-GPT directory, you can run this command on Linux or MacOS:

```
curl -o ./plugins/Auto-GPT-Dolly-Plugin.zip https://github.com/KayLuke/Auto-GPT-Dolly-Plugin/archive/refs/heads/master.zip
```

In PowerShell:

```
Invoke-WebRequest -Uri "https://github.com/KayLuke/Auto-GPT-Dolly-Plugin/archive/refs/heads/master.zip" -OutFile "./plugins/Auto-GPT-Dolly-Plugin.zip"
```

## Configuration

This plugin can be configured via the following .env variables:

- DOLLY_DEBUG (Default=False): Whether to launch the clones with --debug
- DOLLY_CONTINUOUS_LIMIT (Default=5): The maximum number of cycles per clone
- DOLLY_SEPARATE_MEMORY_INDEX (Default=False): Whether to create a separate MEMORY_INDEX env variable for each clone. The separate MEMORY_INDEXes are created by appending the clone's name to the main MEMORY_INDEX 
- DOLLY_SEPARATE_SETTINGS (Default=False): Whether to create a separate settings file and pass it into each clone with --ai-settings commandline variable. The separate settings files will be created by appending the clone's name to the settings file or DOLLY_SETTINGS_TEMPLATE (see below)
- DOLLY_SETTINGS_TEMPLATE (Default=ai_settings_clone_template.yaml): If DOLLY_SEPARATE_SETTINGS is True, this file will be used to create settings files for each clone. It should be placed in the working directory. Within the file, <CLONE_NAME> will be replaced with the name that AutoGPT chooses for the clone, and <CLONE_GOALS> will be replaced with the tasks that AutoGPT wants the clone to perform.
- DOLLY_SEPARATE_INSTRUCTIONS (Default=False): If you're using the wonda prompting technique, this will cause AutoGPT to write the clone's goals to an instrunctions_<CLONE_NAME>.txt file.


## Feedback

Looking forward to your feedback!
