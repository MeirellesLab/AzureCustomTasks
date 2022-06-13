# ACT - Azure Custom Tasks


## About

ACT is a tool to rapidly create custom Tasks for the Microsoft Azure Batch
service to easily support the creation and execution of parallelized jobs.

This tool is perfect to promptly take advantage of this batch cloud environment,
allowing you to create multiple compute node with user defined configurations for
your application, speeding up the deployment and making the Tasks less error prone,
since it's highly reusable and minimizes the code that needs to be done to execute
these Tasks.

## Usage

```bash
python3 azure_custom_tasks.py -j examples/prodigal/config.json -sxw
python3 azure_custom_tasks.py -j prodigal_config.json -s
python3 azure_custom_tasks.py
python3 azure_custom_tasks.py -h
```

## Getting Started

ACT requires the use of Python v3.6 or later and the installation of the required
libraries from the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python),
that can be done as follows:

```bash
pip install -r requirements.txt
```

For more detail, see [Installing ACT page](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/home.md#installation)


## Features

* **Centralized configuration in a JSON file**: instead of making multiple
calls to the Microsoft Azure API for each configuration programmatically.
Making it fast and easy to create batch Tasks.
* **Contain most important Microsoft Azure Batch Service features**: requiring less work to use many
important commands, speeding up access to those features.
* **Automatic mount of storage containers to compute nodes**: the pool configuration can specify the
storage containers to be mounted and teh Tasks can read inputs and write outputs directly to it.
If a resource is commonly used by the Tasks this can cause synchronizing problems that have to be taken into account, for more details see the [blobfusion specifications](https://github.com/Azure/azure-storage-fuse/).
* **Multiple options to define the Task input**: inputs can be blobs in a
storage container or strings in a file. They can also be filtered by existing Tasks
and/or by existing output. Allowing the user to customize the new Tasks creation
for the precise need.
* **Custom function to calculate required computing slots for Tasks**: it's possible to define a function
to calculate the number of required computing slots for each Task, based on the input name and/or size.
Optimizing the resource management and consequently reducing costs.
* **Builtin debug**: to show execution details (inputs/outputs/scripts/task commands) before,
and while, running.
* **Builtin custom log**: to help to keep track of the Task events and
profile the execution of the Task's commands.


## License

This project is licensed under [MIT License](https://github.com/MeirellesLab/AzureCustomTasks/blob/main/LICENSE).

## Contributors

* Author: Pablo Viana
