**This wiki is currently about ACT release v.1.0**

# HOME

Welcome to the ACT wiki. Here you will find information to get you started execution
of Batch Tasks in the Microsoft Azure cloud environment.

* [What is ACT?](#about)
* [Installing ACT](#installation)
* [ACT usage arguments](#act_arguments)
* [ACT configuration file](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/configuration.md)
* [ACT examples:](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/examples.md)
  * [Gene prediction with Prodigal](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/examples.md#1-prodigal)
  * [Splitting gene prediction files](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/examples.md#2-split_files)
  * [Finding Antimicrobial resistance genes with HMMER](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/examples.md#3-hmmer)


## About

ACT is a tool to create custom tasks for the Microsoft Azure batch service to support the creation and execution of parallelized jobs.

This tool is perfect for promptly taking advantage of this batch cloud environment, allowing you to create multiple compute nodes with user-defined configurations for your application, speeding up the deployment and making the Tasks less error prone, since it’s highly reusable and minimizes the code that needs to be done to execute these Tasks.


## Installation

ACT was developed using Python 3 and runs from the command-line (i.e. terminal window in Linux or MacOSX, or at the DOS command-line in Windows). To do that, it requires that you have in your system Python v.3.6 or later versions. To get access to the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python), it is also required the installation of some libraries using the command:

```bash
pip install -r requirements.txt
```

## ACT Arguments

This Section explains arguments that can be used with the ACT program. All arguments are optional and, if not provided, consider the default value:

- **-j or --json** : Use the specified JSON file as the configuration file. This file must be in the .json format and contain all the required configuration strings. If you don’t provide this parameter, the **default value** is to consider the existence of a config.json file in the current working directory. If the json file doesn’t exist, the program finishes with an error message. **You cannot run ACT without a configuration file.** We explain this file and all its parameters in its corresponding [section](https://github.com/MeirellesLab/AzureCustomTasks/blob/main/wiki/configuration.md).
- **-i or --input** : Use the strings in the INPUT file as inputs to each Task. It’s expected that each line contain one input description separated by comma, (1) the input string itself, (2) the input size and (3) the required computing slots for this input, **only the first parameter is required, the other parameters are optional with default value 0 and 1 respectively**. We explain this in more detail in the [example 2](https://github.com/MeirellesLab/AzureCustomTasks/blob/main/wiki/examples.md#2-splitting-files).
- **-x or --exec** : Start the Batch Service, Pool, Job and Tasks, execution with the parameters specified in the configuration file. If you don't supply another **(other then -j and -i)** this is the **default behavior of ACT**.
- **-s or --show** : Show the blobs from the configured containers: input, output and scripts and the tasks commandLine attribute.
- **-sI or --show-inputs** : Show the blobs from the configured container input.
- **-sO or --show-outputs** : Show the blobs from the configured container output.
- **-sS or --show-scripts** : Show the blobs from the configured container scripts.
- **-sT or --show-tasks** : Show the Task's commandLine for each task.
- **-l or --list** : List tasks by their states.
- **-c or --count** : Count tasks by their states.
- **-d or --disable** : Disable the current Job and all associated tasks, returning the Tasks that are running to the end of the execution queue. Cannot add new Tasks while the Job is disabled.
- **-e or --enable** : Enable the current Job and all associated tasks, restarting the Task's allocation to the execution queue.
- **-w or --wait** : Wait all tasks to complete while shows the current progress.
- **-f or --free** : Terminate the batch and free its resources (deleting all Pools, Jobs and Tasks from the Batch Account).
- **-y or --yes** : Include this to --free command to confirm deletion without requering the user reply.
- **-v or --version** : Show program's version number and exit.
- **-h or --help** : Show the help message and exit.


[BACK HOME](#home)
