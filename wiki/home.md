**This wiki is currently about ACT release v.1.0**

# HOME

Welcome to the ACT wiki. Here you will find information to get you started executing Batch Tasks in the Microsoft Azure cloud environment using ACT.

* [What is ACT?](#about)
* [Installing ACT](#installation)
* [ACT usage arguments](#act_arguments)
* [ACT configuration file](configuration.md)
* [ACT examples:](examples.md)
  * [Gene prediction with Prodigal](examples.md#1-prodigal)
  * [Splitting gene prediction files](examples.md#2-split_files)
  * [Finding Antimicrobial resistance genes with HMMER](examples.md#3-hmmer)


## About

ACT is a tool to create custom tasks for the Microsoft Azure Batch Service to support the creation and execution of parallelized jobs.

This tool is perfect for promptly taking advantage of this batch cloud environment, allowing you to create multiple compute nodes with user-defined configurations for your application, speeding up the deployment and making the tasks less error prone, since it is highly reusable and minimizes the code that needs to be done to execute these tasks.

Using ACT is really straight-forward, to get you started you need to install its dependencies and copy the source folder to your computer. Write your task scripts, copy one configuration file from the [examples](examples.md) and change it to reflect your scenario. Place your scripts and inputs accordingly and run the ACT command to start execution.

We invite you to read through this wiki to get more details about ACT usage and features. Also, feel free to [contact us](mailto:pablo.alessandro@gmail.com) if you still have any doubts or run into any bugs.


## Installation

ACT was developed using Python 3 and runs from the command-line (i.e. terminal window in Linux or MacOSX, or at the DOS command-line in Windows). If you don't know if you have Python in your system, check out this [link](https://realpython.com/installing-python/). ACT requires Python v.3.6 or a later version.

To get access to the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python), it is also required the installation of some Azure libraries using the command:

```bash
pip3 install -r requirements.txt
```

or if you have Python3 set as default python command, use:

```bash
pip install -r requirements.txt
```


## ACT Arguments

This Section explains the arguments that can be used with the ACT program. All arguments are optional and if you don't provide some of them assume a default value, which is explained bellow.

Azure Custom Tasks - ACT v1.0
Usage: python3 azure_custom_tasks.py [-j JSON] [-i INPUT] [-xslcedwfyvh] [-sI] [-sO] [-sS] [-sT]


- **-j or --json** : Use the specified JSON file as the configuration file. This file must be in the .json format and contain all the required configuration strings. If you don’t provide this parameter, the **default value** is to consider the existence of a file named **config.json** in the current working directory. If the JSON file doesn’t exist, the program finishes with an error message. **You cannot run ACT without a configuration file.** We explain this file and all its parameters in its corresponding [section](configuration.md) of this wiki.
- **-i or --input** : Use the strings in the INPUT file as inputs for the Tasks. It is expected that each line of this file contains one input description separated by comma, (1) the input string itself, (2) the input size, and (3) the required computing slots for this input, **only the first parameter is required, the other parameters are optional with default value 0 and 1 respectively**. We explain this in more detail in the [example 2](examples.md#2-splitting-files).
- **-x or --exec** : Start the Batch Service, Pool, Job and Tasks, execution with the parameters specified in the configuration file. If you don't supply any argument **(other then -j and -i)** this is the **default behavior of ACT**.
- **-s or --show** : Show the debug information about the current execution: inputs, outputs, scripts and Tasks' commands.
- **-sI or --show-inputs** : Shows the corresponding blobs from configured input.
- **-sO or --show-outputs** : Shows the corresponding blobs from configured output.
- **-sS or --show-scripts** : Shows the corresponding blobs from configured scripts.
- **-sT or --show-tasks** : Shows the Tasks' commandLine for each Task.
- **-l or --list** : List Tasks by their states.
- **-c or --count** : Count Tasks by their states.
- **-d or --disable** : Disable the current Job and all associated Tasks, returning the Tasks that are running to the end of the execution queue. Cannot add new Tasks while the Job is disabled.
- **-e or --enable** : Enable the current Job and all associated Tasks, restarting the Task's allocation to the execution queue.
- **-w or --wait** : Wait all Tasks to complete while showing the current progress.
- **-f or --free** : Terminate the batch and free its resources (deleting all Pools, Jobs and Tasks from the Batch Account).
- **-y or --yes** : Include this to --free command to confirm deletion without requiring user confirmation.
- **-v or --version** : Show ACT version number and exit.
- **-h or --help** : Show the help message and exit.


[BACK HOME](#home)
