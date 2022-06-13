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

ACT is a tool to rapidly create custom Tasks for the Microsoft Azure Batch
service to easily support the creation and execution of parallelized jobs.

This tool is perfect to promptly take advantage of this batch cloud environment,
allowing you to create multiple compute node with user defined configurations for
your application, speeding up the deployment and making the Tasks less error prone,
since it's highly reusable and minimizes the code that needs to be done to execute
these Tasks.

## Installation

ACT requires the use of Python v3.6 or later and the installation of the required
libraries from the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python),
that can be done as follows:

```bash
pip install -r requirements.txt
```

## ACT Arguments

This Section explains in detail the possible arguments used with the ACT program, all arguments are optional and if not provided consider the default value:

- **-j or --json** : uses the specified JSON file as the configuration file. This file must be in the .json format and contain all the required configuration strings. If this parameter is not provided, the **default** is to consider the existence of a config.json in the current working directory, if it doesn't exist the program finishes with an error message. **You cannot run ACT without a configuration file.** This file and all it's configuration parameters are explained in its corresponding [section](#the-configjson-file).
- **-i or --input** : uses the strings in the INPUT file as inputs for each task that will be created. It's expected that each line contain one input description separated by comma, being the first string the input itself, the second the input size and the third the required task slots for this input, **only the first parameter is required, the input string itself, the other parameters are optional with default value 0 and 1 respectively**. This can be understood in more detail in the [examples]().
- **-x or --exec** : start the batch service Pool, Job and tasks execution with the parameters specified in the configuration file. If no other argument is supplied **(other then -j and -i)** this is considered the **default behavior of ACT**.
- **-s or --show** : show the blobs from the configured containers: input, output and scripts and the tasks commandLine attribute.
- **-sI or --show-inputs** : show the blobs from the configured container input.
- **-sO or --show-outputs** : show the blobs from the configured container output.
- **-sS or --show-scripts** : show the blobs from the configured container scripts.
- **-sT or --show-tasks** : show the task's commandLine for each task.
- **-l or --list** : list tasks by their states.
- **-c or --count** : count tasks by their states.
- **-d or --disable** : disable the current Job and all associated tasks, returning the tasks that are running to the end of the execution queue. Cannot add new tasks while the Job is disabled.
- **-e or --enable** : enable the current Job and all associated tasks, restarting the task's allocation to the execution queue.
- **-w or --wait** : wait all tasks to complete while shows the current progress.
- **-f or --free** : terminate the batch and free its resources (deleting all pools, jobs and tasks from the batch account).
- **-y or --yes** : include this to --free command to confirm deletion without requering the user reply.
- **-v or --version** : show program's version number and exit.
- **-h or --help** : show the help message and exit.


[BACK HOME](#home)
