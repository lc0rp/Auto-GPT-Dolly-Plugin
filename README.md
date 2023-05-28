# AutoGPTDolly (Beta) - a cloner plugin for Auto-GTP

## <u>Overview</u>

This plugin adds a "clone_autogpt" command that lets Auto-GPT build an army of powerful minions. AutoGPT can already create AI agents, but sometimes it helps to be able to create additional AutoGTP processes, which can access the tools, plugins and full functionality of AutoGTP.

The "clone_autogpt" command starts a new AutoGPT process, optionally with its own memory, instructions and output files. The processes run in continuous mode for 5 cycles by default. See the Configuration section for how to increase or decrease the number of cycles.

**Concurrency**: As a bonus, the separate processes run concurrently, which can reduce up total execution time for your task.

## <u>Updates!</u>

## **0.2.0 - May 1 2023**

1. **Personality Prompting**
<br/>Dolly now lets you alter the clone personalities using the wellknown BIG 5 personality traits: AKA OCEAN: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism. See: Personality Prompting below.

2. **'Act As' Attributes** 
<br/>Related, you can define a set of attributes for each clone - lazy, witty, talkative, anything goes.

3. **Better Monitoring**
<br/>One key piece of feedback was that it was hard to see what each clone was doing. Now each clone gets their own output and erorr log files. 

## <u>Coming Soon</u>

What am I working on right now? 
- Two way communication with each clone... 
- Separate terminals per clone
- More examples to get you started
- Anything you'd like to see? Let me know!

## <u>Usage Details</u>

This plugin adds a "clone_autogpt" command that starts a new AutoGPT process, optionally with its own memory, instructions and output files. The processes run in continuous mode for 5 cycles by default. See the Configuration section for how to increase or decrease the number of cycles.

---
**GPT 3.5**
~~GPT 3.5 may get confused by the "clone_autogpt" command, and instead try to clone a repository. We provide an alias: "replicate" that seems to work better for GPT 3.5~~~

- Removed from 0.2.0 - may return in a future release.

---
You need EXECUTE_LOCAL_COMMANDS=True

You can tell AutoGPT to clone itself, as part of its tasks:

**Example Goals:**
- Create a clone (choose a name <NAME> for it) to search reddit for "topic" and save the results to reddit_results.txt
- Create a second clone (choose a name <NAME> for it) to download the latest tweets about "topic" and save the results to twitter_results.txt
- Once the files have been created, compare their contents...

**GPT 3.5**
For GPT 3.5, you may have better luck with <NAME> and <GOALS> 

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


## Help and discussion:

Discord: https://discord.com/channels/1092243196446249134/1099609931562369024