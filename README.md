[![DOI](https://zenodo.org/badge/491108327.svg)](https://doi.org/10.5281/zenodo.13937408)

# ACT - Azure Custom Tasks


ACT is a tool to execute customized tasks in the Microsoft Azure Batch Service, supporting the creation and execution of parallelized jobs.

This tool is perfect for promptly taking advantage of this batch cloud environment, allowing you to create multiple compute nodes with user-defined configurations for your application, speeding up the deployment, and making the tasks less error-prone, since it is highly reusable and minimizes the code that needs to be done to execute these tasks.


## Getting Started

ACT requires Python v3.10 or a later version and some libraries of the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python). To install them use the command bellow:

```bash
pip3 install -r requirements.txt
```

For more detail, see [Installing ACT page](https://github.com/MeirellesLab/AzureCustomTasks/wiki#installation)

To see the complete list of ACT running options, check out our [wiki](https://github.com/MeirellesLab/AzureCustomTasks/wiki#installation) or use:

```bash
python3 azure_custom_tasks.py -h
```

## Features

* **Centralized Configuration**: Simplifies deployment by centralizing parameters for Azure Batch resources (Pools, Jobs, Tasks) in a single JSON file, reducing the need for multiple API calls.
* **Comprehensive Azure Batch Support**: Provides streamlined access to essential Azure Batch features, simplifying task management and configuration.
* **Automatic Storage Mounting**: Automatically mounts Azure storage containers to compute nodes, facilitating direct reading and writing of input/output data.
* **Flexible Input Options**: Supports input data as storage blobs or local file strings, with customizable filtering based on task criteria.
* **Custom Resource Management**: Allows users to define functions in the configuration file to calculate required computing slots for tasks, optimizing resource usage and reducing operational costs.
* **Built-in Debugging**: Displays detailed information about task execution (inputs, outputs, scripts, and commands) for troubleshooting.
* **Custom Logging**: Provides detailed logs for monitoring task progress and profiling execution efficiency.


## More Information

* [Wiki Documentation](https://github.com/MeirellesLab/AzureCustomTasks/wiki)


## License

This project is licensed under [MIT License](https://github.com/MeirellesLab/AzureCustomTasks/blob/main/LICENSE).


## Contributors

* Author: [Pablo Viana](http://lattes.cnpq.br/5021260983307628)
