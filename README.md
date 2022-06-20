# ACT - Azure Custom Tasks


ACT is a tool to create custom tasks for the Microsoft Azure Batch Service to support the creation and execution of parallelized jobs.

This tool is perfect for promptly taking advantage of this batch cloud environment, allowing you to create multiple compute nodes with user-defined configurations for your application, speeding up the deployment and making the Tasks less error prone, since it’s highly reusable and minimizes the code that needs to be done to execute these Tasks.


## Getting Started

ACT uses Python v3.6 and requires installing some libraries from the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python). To do so, use the command bellow:

```bash
pip3 install -r requirements.txt
```

or if you have Python3 set as default python command, use:

```bash
pip install -r requirements.txt
```

For more detail, see [Installing ACT page](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/home.md#installation)

To see the complete list of ACT running options, check out our [wiki](https://github.com/MeirellesLab/AzureCustomTasks/blob/main/wiki/home.md) or use:

```bash
python3 azure_custom_tasks.py -h
```

or if you have Python3 set as default python command, use:

```bash
python azure_custom_tasks.py -h
```

## Features

* **Centralizes all configuration parameters in a JSON file**: Instead of making multiple calls to the Microsoft Azure API for each configuration programmatically. Making it fast and easy to create batch Tasks.
* **Contains most important Microsoft Azure Batch Service features**: Providing easy access to many important commands, speeding up usage of those features.
* **Automatically mounts storage containers to compute nodes**: The pool configuration can specify the storage containers to be mounted in the compute nodes and Tasks can read inputs and write outputs to it.
* **Multiple options to define the Task input**: Inputs can be blobs in a storage container or strings in a file. We can also filter them by existing Tasks and/or by existing output. Allowing the user to customize the new Tasks creation for the precise need.
* **Custom function to calculate required computing slots for Tasks**: It’s possible to define, in the configuration file, a function to calculate the number of required computing slots for each Task, based on the input name and/or size. Optimizing the resource management and reducing costs.
* **Built-in debug**: To show execution details (inputs/outputs/scripts/task commands) before, and while, running.
* **Built-in custom log**: To help keep track of the Task events and profile the execution of the Task’s commands.


## More Information

* [Wiki Documentation](https://github.com/MeirellesLab/AzureCustomTasks/blob/main/wiki/home.md)


## License

This project is licensed under [MIT License](https://github.com/MeirellesLab/AzureCustomTasks/blob/main/LICENSE).


## Contributors

* Author: [Pablo Viana](http://lattes.cnpq.br/5021260983307628)
